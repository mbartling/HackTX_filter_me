from flask import Flask
from flask import render_template, request, jsonify
from flask import redirect, url_for, send_file, send_from_directory
from werkzeug import secure_filename
from PIL import Image
import os, subprocess, re

UPLOAD_FOLDER = 'images/'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

CURRENT_IMG = ""
CURRENT_FILTER = ""

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET"])
def index(filename=None):
    print('hello')
    if (CURRENT_IMG is not None):
        print(CURRENT_IMG)
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def get_file_extension(filename):
    return filename.rsplit('.', 1)[1]

@app.route("/img1", methods=["POST"])
def upload_image():
    global CURRENT_IMG
    # get file from POST
    file = request.files['file']

    # check if file id of correct format
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        CURRENT_IMG = filename      
        print CURRENT_IMG  
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        width, height = getImgDimensions(filename)
        return jsonify({
            'imgFolder': app.config['UPLOAD_FOLDER'], 
            'imgName': filename,
            'width': width,
            'height': height
            })
    return "error"

@app.route("/img2", methods=["POST"])
def upload_filter():
    global CURRENT_FILTER
    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        CURRENT_FILTER = filename  
        print CURRENT_FILTER    
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        width, height = getImgDimensions(filename)
        return jsonify({
            'imgFolder': app.config['UPLOAD_FOLDER'], 
            'imgName': filename,
            'width': width,
            'height': height
            })
    return "error"

@app.route("/getNewImage", methods=["POST"])
def getNewImg():
    global CURRENT_IMG
    global CURRENT_FILTER

    CURRENT_IMG = resize(CURRENT_IMG)
    CURRENT_FILTER = resize(CURRENT_FILTER)

    currentImgOnServer = 'images/' + CURRENT_IMG
    currentFilterOnServer = 'images/' + CURRENT_FILTER

    print 'a'
    print CURRENT_IMG
    subprocess.call(["scp", "-i","compute-node-keys.pem", 
        os.path.join(app.config['UPLOAD_FOLDER'], CURRENT_IMG), 
        "ubuntu@ec2-52-27-76-110.us-west-2.compute.amazonaws.com:images/."])
    print 'b'
    subprocess.call(["scp", "-i","compute-node-keys.pem", 
        os.path.join(app.config['UPLOAD_FOLDER'], CURRENT_FILTER), 
        "ubuntu@ec2-52-27-76-110.us-west-2.compute.amazonaws.com:images/."])
    print 'c'
    subprocess.call(["ssh", "-i", "compute-node-keys.pem", 
        "ubuntu@ec2-52-27-76-110.us-west-2.compute.amazonaws.com", 
        "rm", "-f", "images/out.png"])
    subprocess.call(["ssh", "-i", "compute-node-keys.pem", 
        "ubuntu@ec2-52-27-76-110.us-west-2.compute.amazonaws.com", 
        "python", "HackTX_filter_me/neural_artistic_style/neural_artistic_style.py", 
        "--subject", currentImgOnServer, "--style", currentFilterOnServer, 
        "--iterations", "75", "--output", "images/out.png"])
    print 'd'
    subprocess.call(["scp", "-i", "compute-node-keys.pem", 
        "ubuntu@ec2-52-27-76-110.us-west-2.compute.amazonaws.com:images/out.png"])
    print 'e'
    return jsonify({
        'data': 'data'
        })


@app.route("/images/<filename>")
def uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print e
        return redirect(url_for('index'))

def getImgDimensions(filename):
    image = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    (width, height) = image.size
    return width, height

def resize(filename):
    max_size = (1024,1024)

    image = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    out_image = re.sub("\.", "_transformed.", filename)

    image.thumbnail(max_size, Image.ANTIALIAS)
    image.save(out_image)
    return out_image

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=80)
