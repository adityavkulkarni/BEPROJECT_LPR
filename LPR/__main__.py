from flask import Flask, render_template, request, Markup
import cv2 
from Vehicle_detect import detect_img
import numpy as np
from rtovehicle import get_vehicle_details
from Database import  *
import os
app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'


@app.route('/')
def upload_img():
    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # read image file string data
        filestr = request.files['file'].read()
        # convert string data to numpy array
        npimg = np.fromstring(filestr, np.uint8)
        # convert numpy array to image
        img = cv2.imdecode(npimg, cv2.IMREAD_LOAD_GDAL)
        text = ""
        #cv2.imwrite('http://localhost:5000/static/uploaded.jpg', img)
        time, text, image = detect_img(fname=img, cnt=0)
        #stat , msg = get_from_db(text)
        stat = False
        msg='Data not found in database.<br> <p style="color:  red  ;">!!!!#### Vehicle does not belongs to the premises ####!!!! <br>Fetched Record from RTO </p>  '
        s=''
        cv2.imwrite('detected.jpg', image)
        if stat:
            s = msg
        else:
		
            df = get_vehicle_details(text)
            print(df)
            if(df.iloc[0,0]=='reject'):
                s =  'Number Plate Not found'

            else:
                s = '<h2>'+msg+'</h2>'+df.to_html()

        return render_template('upload.html', type2='', tab=Markup(s))
'''
@app.route('/show')
def show():
    app.config['UPLOAD_FOLDER'] = '/home/aditya/sih/sih_flask/static/'
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'detected.jpg')
    return render_template('home.html', user_image =full_filename )
'''
app.run()
