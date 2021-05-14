from typing import List, Any
import pytesseract
from PIL import Image
import cv2
import numpy as np
import timeit
from paths import *
import re


def get_roi(image, x, y, width, height):
    roi = (image[y:y + height, x:x + width])
    return roi


def read_num(fname):
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    text = pytesseract.image_to_string(Image.fromarray(fname))
    return check_txt(text)


def put_text(image, dim, txt):
    cv2.rectangle(image, (dim[0], dim[1]), (dim[0] + dim[2], dim[1] + dim[3]), (0, 255, 0), 2)
    cv2.putText(image, txt, org=(dim[0], dim[1] - 15), fontFace=cv2.FONT_HERSHEY_COMPLEX,
                fontScale=0.75, color=(0, 255, 0), thickness=2)
    return image


def check_txt(txt):
    txt = re.sub('[^A-Za-z0-9]+', '', txt)
    return txt


def get_object(image, model):
    img = image
    height, width, channels = img.shape
    roi: List[Any] = []

    if model == 'lapi':
        net = cv2.dnn.readNet(LAPI_WEIGHT_PATH, LAPI_CFG_PATH)
    elif model == 'yolo':
        net = cv2.dnn.readNet(YOLO_WEIGHT_PATH, YOLO_CFG_PATH)
    else:
        return

    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    net.setInput(blob)
    outs = net.forward(output_layers)
    stat = False
    class_ids = []
    confidences = []
    boxes = []
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

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    dims = []
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            # label = str(classes[class_ids[i]])
            color = [0, 255, 0]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            roi.append(get_roi(image, x, y, w, h))
            dims = [x, y, w, h]
    return stat, roi, img, dims


def detect_img(image, cnt, op='Output'):
    start = timeit.default_timer()

    veh_path = IMAGE_OUTPUT_DIR + op + '_' + str(cnt) + '.jpg'
    stat_v, roi, image, dim = get_object(image, model='yolo')
    if stat_v:
        cv2.imwrite(veh_path, image)

    txt = ''
    stat, plates, img, dim = get_object(image, model='lapi')
    fin1 = img
    if stat:
        for j in range(len(plates)):
            txt = read_num(plates[j])
            im = put_text(image, dim, txt)
            cv2.imwrite(IMAGE_OUTPUT_DIR + 'fin.jpg', im)
            fin1 = im
            print('PLATE FOUND\nTEXT: ' + txt)
    stop = timeit.default_timer()
    print("TIME:" + str(stop - start))
    return txt, fin1


def detect_vid(fname, output='Output', skip=1):
    i = 0
    start = timeit.default_timer()
    # bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
    cap = cv2.VideoCapture(fname)

    while cap.isOpened():
        # bar.update(i)
        ret, frame = cap.read()
        if i == 0:
            fshape = frame.shape
            fheight = fshape[0]
            fwidth = fshape[1]
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(os.getcwd() + '/op/video/' + output + '.avi', fourcc, 10.0,
                                  (fwidth, fheight))
            i = i + 1

        if ret:
            img = proc_vid(frame, i)
            # out.write(img)
            # cv2.imshow('frame', img)  # show the video
            i = i + skip

            cap.set(1, i)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    stop = timeit.default_timer()

    cap.release()
    cv2.destroyAllWindows()

    return stop - start


def proc_vid(image, cnt):
    veh_path = VIDEO_OUTPUT_DIR + '_' + str(cnt) + '.jpg'
    stat_v, roi, image, dim = get_object(image, model='yolo')
    if stat_v:
        print('\nVEHICLE FOUND')
        cv2.imwrite(veh_path, image)
    '''s, plates, img, dim = get_plate(image)


    for i in range(len(plates)):
        cv2.imwrite('/home/aditya/sih/sih_cb31/op/video/plates/pl_'+str(i)+'_'+str(cnt)+'.jpg',plates[i])
       # print('\nPLATE FOUND')
        txt = read_num(plates[i])
        img = put_text(img, dim, txt,i)
    if s:
        cv2.imwrite(veh_path, img)
        c'''
    return image
