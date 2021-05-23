import os
import random
import datetime
random.seed(2)

YOLO_WEIGHT_PATH = os.getcwd()+'/model/yolov3.weights'
YOLO_CFG_PATH = os.getcwd()+'/model/yolov3.cfg'

LAPI_WEIGHT_PATH = os.getcwd()+'/model/lapi.weights'
LAPI_CFG_PATH = os.getcwd()+'/model/lapi.cfg'
LAPI_NAMES_PATH = os.getcwd()+'/model/lapi_class.names'

IMAGE_OUTPUT_DIR = os.getcwd()+'/op/img/'
VIDEO_OUTPUT_DIR = os.getcwd()+'/op/vid/'

TEMP_DIR_PATH = os.getcwd()+'/static/tempdata/'

STATIC_TEMP_DIR_PATH = '/static/tempdata/'

#TESSERACT_PATH = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

RANDOM = str(random.random())

# Database paths
MASTER_DB_PATH = 'db/master.db'
def TIMESTAMP():
    time = datetime.datetime.now()
    return time.strftime("%Y%m%d#%H:%M:%S")

if __name__=='__main__':
    print(TEMP_DIR_PATH)
