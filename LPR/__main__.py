import glob
from flask import Flask, render_template, request, Markup
import cv2
import paths
from Vehicle_detect import detect_img
import numpy as np
from paths import *
import Database as db

app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'

flag = None
num = None

@app.route('/')
def index():
    files = glob.glob(TEMP_DIR_PATH+'*')
    for f in files:
        os.remove(f)
    return render_template('index.html',static_url_path='/static')

@app.route('/details')
def render_details():
        return render_template('details.html')

@app.route('/showhistory')
def render_history():
        return render_template('showhistory.html', parent_list=db.get_history_data())

@app.route('/vehicleinfo', methods=['GET', 'POST'])
def render_vehicle_info():
    if request.method == 'POST':
        id = request.form['vehicle_id']
        img = db.get_image_data(id)
        return render_template('viewinfo_image.html')
    return render_template('viewinfo.html')

## ADD NEW VEHICLE INFO
@app.route('/addavehicle', methods=['GET', 'POST'])
def render_addavehicle():
    if request.method == 'POST':
        id = request.form['vehicleno']
        name = request.form['name']
        contact_no = request.form['contactno']
        address = request.form['address']
        db.insert_data(id,name,contact_no,address)
        return render_template('addavehicle.html' )
    else:
        global flag, num
        return render_template('addavehicle.html', flag=flag, num=num)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file1():
    return render_template('vehicle.html', type2='', tab="")

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        filestr = request.files['file'].read()
        npimg = np.fromstring(filestr, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_LOAD_GDAL)
        text, image = detect_img(image=img, cnt=0)

        cur_name = 'detected_' + TIMESTAMP() + '.png'
        cv2.imwrite(TEMP_DIR_PATH + cur_name, image)
        msg='<h1> Text from Image: '+text+'</h1>'
        if len(text)<1  :
            print("Number Plate not detected")
            db.insert_history_data(0,cur_name)
            return render_template('warning.html', static_url_path='/static',name ='tempdata/'+cur_name)

        #Database.create_connection(MASTER_DB_PATH)
        data = db.get_details(text)
        if data is not None:
            cv2.imwrite(IMAGE_OUTPUT_DIR + 'detected_' + paths.TIMESTAMP() + '.jpg', image)
            db.insert_history_data(1,cur_name)
            return render_template('vehicle.html', type2='', tab=Markup(data.to_html(classes='table')))
        else:
            print("Data not in DB")
            global flag, num
            num = text
            flag = 'true'
            cv2.imwrite(IMAGE_OUTPUT_DIR + 'detected_' + paths.TIMESTAMP() + '.jpg', image)
            db.insert_history_data(2,cur_name)
            return render_template('warning.html', static_url_path='/static',name ='tempdata/'+cur_name, enable='true')

app.run(port=8986)
