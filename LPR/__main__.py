from flask import Flask, render_template, request, Markup,url_for, redirect
import cv2 
from Vehicle_detect import detect_img
import numpy as np
from paths import *
app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'

@app.route('/')
def index():
    return render_template('index.html',static_url_path='/static')

@app.route('/details')
def render_details():
        return render_template('details.html')

@app.route('/showhistory')
def render_history():
        return render_template('showhistory.html')

@app.route('/addavehicle')
def render_addavehicle():
        return render_template('addavehicle.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file1():
    return render_template('vehicle.html', type2='', tab="")

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # read image file string data
        filestr = request.files['file'].read()
        # convert string data to numpy array
        npimg = np.fromstring(filestr, np.uint8)
        # convert numpy array to image
        img = cv2.imdecode(npimg, cv2.IMREAD_LOAD_GDAL)
        text, image = detect_img(image=img, cnt=0)
        #stat , msg = get_from_db(text)
        msg='<h1> Text from Image: '+text+'</h1>'
        cv2.imwrite(IMAGE_OUTPUT_DIR+'detected.jpg', image)
        return render_template('vehicle.html', type2='', tab=Markup(msg))

app.run()
