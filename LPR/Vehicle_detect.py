import re
import timeit
from typing import List, Any

import cv2
import numpy as np
import pytesseract
from PIL import Image

import paths
from ocr_api import image_to_string
from paths import *


def get_roi(image, x, y, width, height):
    '''
    Crops the image in specifed dimensions
    :param image: image file
    :param x: x coordinate of center of ROI
    :param y: y coordinate of center of ROI
    :param width: width of ROI
    :param height: height of ROI
    :return: Sliced image
    '''
    roi = (image[y:y + height, x:x + width])
    return roi


def read_num(fname, mode='tesseract'):
    '''
    Extract text from image
    :param fname: path where image is stored
    :param mode: OCR model (tesseract/api)
    :return: Cleaned text extracted from image
    '''
    text = ''
    if mode == 'tesseract':
        #pytesseract.pytesseract.tesseract_cmd = paths.TESSERACT_PATH
        text = pytesseract.image_to_string(Image.fromarray(fname))
    else:
        Image.fromarray(fname).save(OCR_TEMP_DIR_PATH + 'temp.png')
        text = image_to_string(OCR_TEMP_DIR_PATH + 'temp.png')
    return clean_text(text)


def put_text(image, dim, txt):
    '''
    Draws a rectangle and writes the provided text on the image
    :param image: image file
    :param dim: dimensions of rectangle (x,y,w,h)
    :param txt: text to write
    :return: image file with rectangle and text
    '''
    cv2.rectangle(image, (dim[0], dim[1]), (dim[0] + dim[2], dim[1] + dim[3]), (0, 255, 0), 2)
    cv2.putText(image, txt, org=(dim[0], dim[1] - 15), fontFace=cv2.FONT_HERSHEY_COMPLEX,
                fontScale=0.75, color=(0, 255, 0), thickness=2)
    return image


def clean_text(txt):
    '''
    Removes spaces and punctuation from text
    :param txt: text to be cleaned
    :return: cleaned text
    '''
    txt = re.sub('[^A-Za-z0-9]+', '', txt)
    return txt


def get_object(image, model,draw_on_image = True):
    '''
    Gets vehicle/number plate from image
    :param image: image file
    :param model: object to detect (vehicle[yolo]/number plate[lapi)
    :param draw_on_image: True if we want text on image
    :return  stat: presence of object (True/False)
    :return  roi: sliced image containing object
    :return  img: image file with object markings
    :return  dims: dimension of region in which object is present
    '''
    img = image
    height, width, channels = img.shape
    roi: List[Any] = []
    ## Select model
    if model == 'lapi':
        net = cv2.dnn.readNet(LAPI_WEIGHT_PATH, LAPI_CFG_PATH)
    elif model == 'yolo':
        net = cv2.dnn.readNet(YOLO_WEIGHT_PATH, YOLO_CFG_PATH)
    else:
        return

    ## Load model and prepare image
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    stat = False
    class_ids = []
    confidences = []
    boxes = []
    ## Loop over results and store them in variable based on confidence
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int((detection[2] * width) + 10)
                h = int((detection[3] * height) + 10)
                stat = True
                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    ## Draw rectangle to mark objects
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    dims = []
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            # label = str(classes[class_ids[i]])
            color = [0, 255, 0]
            if draw_on_image :cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            roi.append(get_roi(image, x, y, w, h))
            dims = [x, y, w, h]
    return stat, roi, img, dims


def detect_img(image,draw_on_image = True):
    '''
    Gets the text from image (wrapper on all functions in this file)
    :param image: image file
    :param draw_on_image: True if we want text on image
    :return text: detected text from image
    :return image: marked image
    '''
    start = timeit.default_timer()
    text = ''
    ## Get vehicle and number plate
    stat_v, roi, image, dim = get_object(image, model='yolo',draw_on_image=draw_on_image)
    stat, plates, image, dim = get_object(image, model='lapi',draw_on_image=draw_on_image)
    ## Mark them in image
    if stat:
        for j in range(len(plates)):
            text = read_num(plates[j])
            if draw_on_image : image = put_text(image, dim, text)
            print('PLATE FOUND\nTEXT: ' + text)
    stop = timeit.default_timer()
    print("TIME:" + str(stop - start))
    return text, image
