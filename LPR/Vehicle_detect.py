from typing import List, Any
import pytesseract
from PIL import Image
import cv2 
import numpy as np
import  timeit
#import  progressbar
import requests
import  json
import re

def  get_plate(image):
    img = image
    height, width, channels = img.shape
    ROI: List[Any] = []
    net = cv2.dnn.readNet('/home/aditya/BEP/LPR/model/lapi.weights',
                          '/home/aditya/BEP/LPR/model/lapi.cfg')
    coco_name = '/home/aditya/BEP/LPR/model/lapi_class.names'
    with open(coco_name, "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    net.setInput(blob)
    outs = net.forward(output_layers)
    stat =False
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
                w = int((detection[2] * width)+10)
                h = int((detection[3] * height)+10)
                stat = True
                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    xywh=[]
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            # label = str(classes[class_ids[i]])
            color = [0, 255, 0]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            ROI.append(roi(image, x, y, w, h))
            xywh = [x,y,w,h]
    return stat,ROI, img,xywh



def  get_vehicle(image):
    img = image
    height, width, channels = img.shape
    ROI: List[Any] = []
    net = cv2.dnn.readNet('/home/aditya/BEP/LPR/model/yolov3.weights',
                          '/home/aditya/BEP/LPR/model/yolov3.cfg')
    stat = False
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            #if class_id == 'car' or class_id == 'truck' or class_id == 'bus' or class_id =='motorbike':
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                stat = True
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    xywh = []
    for i in range(len(boxes)) :
        if i in indexes:
            x, y, w, h = boxes[i]
            # label = str(classes[class_ids[i]])
            color = [0, 255, 0]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            ROI.append(roi(image, x, y, w, h))
            xywh.append([x, y, w, h])
    return stat,ROI, img,xywh


def roi(image, x, y, width, height):
    ROI = (image[y:y + height, x:x + width])
    return ROI


def read_num(fname):
    # pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'


    text = pytesseract.image_to_string(Image.fromarray(fname))
    return check_txt(text)

def put_text(image,dim,txt,i):

    cv2.rectangle(image, (dim[0], dim[1]), (dim[0] + dim[2], dim[1] + dim[3]), (0,255,0), 2)
    cv2.putText(image,(txt),org=(dim[0],dim[1]-15),fontFace=cv2.FONT_HERSHEY_COMPLEX,fontScale=0.75,color=(0,255,0),thickness=2)
    #cv2.imwrite('/home/aditya/sih/sih_cb31/op/numplate' + str(i) + '.jpg', image)
    return  image

def check_txt(txt):
    txt = re.sub('[^A-Za-z0-9]+', '', txt)
    return txt
def detect_vid(fname, output='Output',skip=1):
    i = 0
    start = timeit.default_timer()
   # bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
    cap = cv2.VideoCapture(fname)

    while (cap.isOpened()):
        #bar.update(i)
        ret, frame = cap.read()
        if i == 0:
            fshape = frame.shape
            fheight = fshape[0]
            fwidth = fshape[1]
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter('/home/aditya/sih/sih_cb31/op/video/' + output + '.avi', fourcc, 10.0,
                                  (fwidth, fheight))
            i = i + 1

        if ret == True:
            img = proc_vid(frame,i)
            #out.write(img)
            #cv2.imshow('frame', img)  # show the video
            i = i + skip

            cap.set(1, i)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    stop = timeit.default_timer()

    cap.release()
    cv2.destroyAllWindows()


    return (stop - start)

def detect_img(fname,cnt,op='Output'):
    start = timeit.default_timer()
    veh_path = '/home/aditya/sih/sih_cb31/op/veh/'+op+'_'+str(cnt)+'.jpg'

    image1 = fname
    #image1 = cv2.imread(fname)
    stat_v, roi, image, dim = get_vehicle(image1)
    if stat_v:
        #print('VEHICLE FOUND')
        cv2.imwrite(veh_path, image)

    txt=''
    stat, plates, img, dim = get_plate(image1)
    fin1 = img
    if stat:
        #cv2.imwrite('/home/aditya/sih/sih_cb31/op/vehicle_pl'+str(cnt)+'.jpg', img)
        for j in range(len(plates)):
            pl_path = '/home/aditya/sih/' + op + '_' + str(cnt) + '_' + str(j) + '.jpg'
            fin_path = '/home/aditya/sih/' + op + '_' + str(cnt) + '_' + str(j) + '.jpg'
            #cv2.imwrite(pl_path, plates[j])
            

            txt = read_num(plates[j])

            im = put_text(image, dim, txt,j)
            #cv2.imwrite(fin_path, im)
            fin1 = im
            #print('PLATE FOUND\nTEXT: '+txt)
    stop = timeit.default_timer()
    return  (stop-start),txt,fin1


def proc_vid(image,cnt):
    veh_path = '/home/aditya/sih/sih_cb31/op/video/veh/' + '_' + str(cnt) + '.jpg'
    stat_v, roi, image, dim = get_vehicle(image)
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
    return  image



'''
def find_rect(image):
    grayScale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Find edges in the image using canny edge detection method
    # Calculate lower threshold and upper threshold using sigma = 0.33
    sigma = 0.33
    v = np.median(grayScale)
    low = int(max(0, (1.0 - sigma) * v))
    high = int(min(255, (1.0 + sigma) * v))

    edged = cv2.Canny(grayScale, low, high)

    # After finding edges we have to find contours
    # Contour is a curve of points with no gaps in the curve
    # It will help us to find location of shapes

    # cv2.RETR_EXTERNAL is passed to find the outermost contours (because we want to outline the shapes)
    # cv2.CHAIN_APPROX_SIMPLE is removing redundant points along a line
    (cnts, _) = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)


     

    # Now we will loop over every contour
    # call detectShape() for it and
    # write the name of shape in the center of image

    # loop over the contours
    rects = []
    i = 0
    img = image
    for c in cnts:

        tr, area, a = isrect(c)
        # Outline the contours
        if tr and (area > 1000):
            rects.append(a)
            cv2.drawContours(image, [c], -1, (0, 255, 0), 2)

            #cv2.rectangle(img, (a[0], a[1]), (a[0] + a[2], a[1] + a[3]), (0,255,255), 2)

        # Write the name of shape on the center of shapes
        # cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
        # 0.5, (255, 255, 255), 2)

        # show the output image
    return img, rects,a


def isrect(c):

    # calculate perimeter using
    peri = cv2.arcLength(c, True)
    area = 0
    # apply contour approximation and store the result in vertices
    vertices = cv2.approxPolyDP(c, 0.04 * peri, True)
    stat = False
    # If the shape it triangle, it will have 3 vertices
    # if the shape has 4 vertices, it is either a square or
    # a rectangle
    a = []
    if len(vertices) == 4:
        # using the boundingRect method calculate the width and height
        # of enclosing rectange and then calculte aspect ratio

        x, y, width, height = cv2.boundingRect(vertices)

     #  aspectRatio = float(width) / height

        #if aspectRatio >= 0.95 and aspectRatio <= 1.05:
           # shape = "square"
        #else:
           # shape = "rectangle
        stat = True
        area = width * height
        a = [x, y, width, height]

    return stat, area, a
'''
'''def detect_img(fname,cnt):
    start = timeit.default_timer()

    image1 = cv2.imread(fname)

    image = image1
    txt=''
    regions, img,dim1 = get_vehicle(image)
    cv2.imwrite('/home/aditya/sih/sih_cb31/op/vehicle'+str(cnt)+'.jpg', img)
    for i in range(len(regions)):
        cv2.imwrite('/home/aditya/sih/sih_cb31/op/vl'+str(cnt)+'_' + str(i) + '.jpg', regions[i])
        stat, plates, img, dim = get_plate(regions[i])
        if stat:
            cv2.imwrite('/home/aditya/sih/sih_cb31/op/vehicle_pl'+str(cnt)+'.jpg', img)
            for j in range(len(plates)):
                cv2.imwrite('/home/aditya/sih/sih_cb31/op/pl'+str(cnt)+'_' + str(j) + '.jpg', plates[j])
                txt = read_num(plates[j])
                im = put_text(img, dim, txt)
                cv2.imwrite('/home/aditya/sih/sih_cb31/op/ final'+str(j)+''+str(cnt)+'.jpg', im)
    stop = timeit.default_timer()
    return  (stop-start),txt
'''
