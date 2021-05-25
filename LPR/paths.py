import datetime
import os
import random

random.seed(2)

YOLO_WEIGHT_PATH = os.getcwd() + '/model/yolov3.weights'
YOLO_CFG_PATH = os.getcwd() + '/model/yolov3.cfg'

LAPI_WEIGHT_PATH = os.getcwd() + '/model/lapi.weights'
LAPI_CFG_PATH = os.getcwd() + '/model/lapi.cfg'
LAPI_NAMES_PATH = os.getcwd() + '/model/lapi_class.names'

IMAGE_OUTPUT_DIR = os.getcwd() + '/op/img/'
VIDEO_OUTPUT_DIR = os.getcwd() + '/op/vid/'

TEMP_DIR_PATH = os.getcwd() + '/static/tempdata/'

OCR_TEMP_DIR_PATH = os.getcwd() + '/temp_ocr/'

STATIC_TEMP_DIR_PATH = '/static/tempdata/'

TESSERACT_PATH = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

MASTER_DB_PATH = 'db/master.db'

RANDOM = str(random.random())


def TIMESTAMP():
    '''
    Generates timestamp
    :return: timestamp in '20210525#17:59:13' format
    '''
    time = datetime.datetime.now()
    return time.strftime("%Y%m%d#%H:%M:%S")


def clean_timestamp(timestamp):
    '''
    Cleans timestamp in readable form
    :param timestamp: timestamp in '20210525#17:59:13' format
    :return:  time stamp in 'Date: 25 May 2021 Time: 17:59:19' format
    '''
    datem = datetime.datetime.strptime(timestamp, "%Y%m%d#%H:%M:%S")
    return "Date: " + str(datem.day) + " " + str(datem.strftime("%B")) + " " + str(datem.year) + \
           "  Time: " + str(datem.hour) + ":" + str(datem.minute) + ":" + str(datem.second)


if __name__ == '__main__':
    print(TEMP_DIR_PATH)
