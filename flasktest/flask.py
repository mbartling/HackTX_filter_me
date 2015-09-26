import flask from Flask
import render_template from flask

app = Flask(__name__)
@app.route('/')
def hello():
	return render_template("index.html")
