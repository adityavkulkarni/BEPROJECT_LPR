'''
PROJECT EXPLANATION
'''
import glob

import cv2
import numpy as np
from flask import Flask, render_template, request
import os

import Database as db
import paths
from Vehicle_detect import detect_img
from paths import IMAGE_OUTPUT_DIR,TEMP_DIR_PATH,TIMESTAMP,clean_timestamp

## Initiate App
app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'

## Set global flags and refresh temp directory
for f in glob.glob(TEMP_DIR_PATH + '*'):
    os.remove(f)
FLAG = None
NUM = None
IS_HISTORY_UPDATED = False
HISTORY = db.get_history_data()



@app.route('/')
def index():
    '''
    Render homepage
    URL - localhost:port/
    '''
    return render_template('index.html',
                           static_url_path='/static')

@app.route('/details')
def render_details():
    '''
    Render project details(Read More) page
    URL - localhost:port/details
    '''
    return render_template('details.html')


@app.route('/showhistory')
def render_history():
    '''
    Render history page
    URL - localhost:port/showhistory
    '''
    global HISTORY, IS_HISTORY_UPDATED
    if IS_HISTORY_UPDATED:
        HISTORY = db.get_history_data()
    return render_template('showhistory.html',
                           parent_list=HISTORY)


@app.route('/addavehicle', methods=['GET', 'POST'])
def render_addavehicle():
    '''
     Render add vehicle page
     URL - localhost:port/addavehicle
    '''
    if request.method == 'POST':
        ## Get data from form
        vehicle_id = request.form['vehicleno']
        name = request.form['name']
        contact_no = request.form['contactno']
        address = request.form['address']
        ## Insert data into db
        db.insert_data(vehicle_id, name, contact_no, address)
        return render_template('addavehicle.html')
    else:
        ## For recieving redirect from warning page
        global FLAG, NUM
        return render_template('addavehicle.html',
                               flag=FLAG,
                               num=NUM)
@app.route('/upload', methods=['GET', 'POST'])
def upload_pre():
    '''
    Render upload vehicle page
     URL - localhost:port/upload
    '''
    return render_template('upload.html',
                           type2='',
                           tab="")

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    '''
     Render upload vehicle page
     URL - localhost:port/uploader
    '''
    global IS_HISTORY_UPDATED
    if request.method == 'POST':
        ## Get image from form
        filestr = request.files['file'].read()
        npimg = np.fromstring(filestr, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_LOAD_GDAL)

        ## Get text and marked image from OCR
        text, image = detect_img(image=img,draw_on_image = False)
        cur_name = 'detected_' + TIMESTAMP() + '.png'
        cv2.imwrite(TEMP_DIR_PATH + cur_name, image)

        ## If number plate not detected - pass to warning page
        if len(text) < 1:
            print("Number Plate not detected")
            db.insert_history_data(0, cur_name)
            IS_HISTORY_UPDATED = True
            return render_template('warning.html',
                                   static_url_path='/static',
                                   name='tempdata/' + cur_name,
                                   time=clean_timestamp(TIMESTAMP()))

        ## If number plate detected - check database
        data = db.get_details(text)
        if data is not None:
            ## If number plate present in databse - go to view vehicle info page
            cv2.imwrite(IMAGE_OUTPUT_DIR + 'detected_' + paths.TIMESTAMP() + '.jpg', image)
            db.insert_history_data(1, cur_name)
            IS_HISTORY_UPDATED = True
            return render_template('vehicleinfo.html',
                                   type2='',
                                   licence=data[0],
                                   name =data[1],
                                   address=data[3] ,
                                   contact= data[2],
                                   time=clean_timestamp(TIMESTAMP()),
                                   image='tempdata/' + cur_name)
        else:
            ## If number plate not present in database - go to warning page
            global FLAG, NUM
            NUM = text
            FLAG = 'true'
            cv2.imwrite(IMAGE_OUTPUT_DIR + 'detected_' + paths.TIMESTAMP() + '.jpg', image)
            db.insert_history_data(2, cur_name)
            IS_HISTORY_UPDATED = True
            return render_template('warning.html',
                                   static_url_path='/static',
                                   name='tempdata/' + cur_name,
                                   enable='true',
                                   time=clean_timestamp(TIMESTAMP()))

@app.route('/historydetails/<path>', methods=['GET', 'POST'])
def historydetails(path):
    print(path.replace('*','/'))
    text, image = detect_img(image=cv2.imread(os.curdir+path.replace('*','/'))
                             , draw_on_image = False)
    cur_name = 'detected_' + TIMESTAMP() + '.png'
    cv2.imwrite(TEMP_DIR_PATH + cur_name, image)

    ## If number plate not detected - pass to warning page
    if len(text) < 1:
        print("Number Plate not detected")
        return render_template('warning.html',
                               static_url_path='/static',
                               name='tempdata/' + cur_name,
                               time=clean_timestamp(TIMESTAMP()))

    ## If number plate detected - check database
    data = db.get_details(text)
    if data is not None:
        return render_template('vehicleinfo.html',
                               type2='',
                               licence=data[0],
                               name=data[1],
                               address=data[3],
                               contact=data[2],
                               time=clean_timestamp(TIMESTAMP()),
                               image='tempdata/' + cur_name)
    else:
        ## If number plate not present in database - go to warning page
        global FLAG, NUM
        NUM = text
        FLAG = 'true'
        return render_template('warning.html',
                               static_url_path='/static',
                               name='tempdata/' + cur_name,
                               enable='true',
                               time=clean_timestamp(TIMESTAMP()))


## Run app on specified port
if __name__=='__main__':
    app.run(port=8986)
