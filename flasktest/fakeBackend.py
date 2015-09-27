from flask import Flask
from flask import render_template, request, jsonify
from flask import redirect, url_for, send_file, send_from_directory
from werkzeug import secure_filename
import os

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
    # get file from POST
    file = request.files['file']

    # check if file id of correct format
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        CURRENT_IMG = filename        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #return redirect(url_for('uploaded_file', filename=filename))
        return jsonify({
            'imgFolder': app.config['UPLOAD_FOLDER'], 
            'imgName': filename
            })
    return "error"

@app.route("/img2", methods=["POST"])
def upload_filter():
    file = request.files['file']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        CURRENT_FILTER = filename      
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #return redirect(url_for('uploaded_file', filename=filename))
        return jsonify({
            'imgFolder': app.config['UPLOAD_FOLDER'], 
            'imgName': filename
            })
    return "error"

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    print 'hello'
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print e
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()