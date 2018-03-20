"""
parse PASCAL VOC xml annotations
"""

import os
import sys
import xml.etree.ElementTree as ET
import glob
import json
import cv2
def _pp(l): # pretty printing 
    for i in l: print('{}: {}'.format(i,l[i]))

def pascal_voc_clean_xml(ANN, pick, exclusive = False):
    print('Parsing for {} {}'.format(
            pick, 'exclusively' * int(exclusive)))

    dumps = list()
    cur_dir = os.getcwd()
    os.chdir(ANN)
    annotations = os.listdir('.')
    annotations = glob.glob(str(annotations)+'*.xml')
    size = len(annotations)

    for i, file in enumerate(annotations):
        # progress bar      
        sys.stdout.write('\r')
        percentage = 1. * (i+1) / size
        progress = int(percentage * 20)
        bar_arg = [progress*'=', ' '*(19-progress), percentage*100]
        bar_arg += [file]
        sys.stdout.write('[{}>{}]{:.0f}%  {}'.format(*bar_arg))
        sys.stdout.flush()
        
        # actual parsing 
        in_file = open(file)
        tree=ET.parse(in_file)
        root = tree.getroot()
        jpg = str(root.find('filename').text)
        imsize = root.find('size')
        w = int(imsize.find('width').text)
        h = int(imsize.find('height').text)
        all = list()

        for obj in root.iter('object'):
                current = list()
                name = obj.find('name').text
                if name not in pick:
                        continue

                xmlbox = obj.find('bndbox')
                xn = int(float(xmlbox.find('xmin').text))
                xx = int(float(xmlbox.find('xmax').text))
                yn = int(float(xmlbox.find('ymin').text))
                yx = int(float(xmlbox.find('ymax').text))
                current = [name,xn,yn,xx,yx]
                all += [current]

        add = [[jpg, [w, h, all]]]
        dumps += add
        in_file.close()

    # gather all stats
    stat = dict()
    for dump in dumps:
        all = dump[1][2]
        for current in all:
            if current[0] in pick:
                if current[0] in stat:
                    stat[current[0]]+=1
                else:
                    stat[current[0]] =1

    print('\nStatistics:')
    _pp(stat)
    print('Dataset size: {}'.format(len(dumps)))

    os.chdir(cur_dir)
    return dumps

def parse_annotation(ANN, IMGDIR):
    print('Parsing using user defined function')
    dumps = list()
    ann_file = os.path.join(ANN ,'comb-label.idl')
    img_dir = IMGDIR
    with open(ann_file) as f:
        lines = f.readlines()

    for each in lines:
        all = list()
        line = json.loads(each) 
        
        image_name = list(line.keys())[0]
        if not list(line.values())[0]: # no label in annotation
            # print("No label in this image")
            continue
        else:
            for box in list(line.values())[0]:        
                xmin = box[0]
                ymin = box[1]
                xmax = box[2]
                ymax = box[3]
                label = box[4]
                current = [str(label), xmin, ymin, xmax, ymax]
                all += [current]
        img_path = os.path.join(img_dir, image_name )   
        img = cv2.imread(img_path)  
        h, w = img.shape[0], img.shape[1]    
        # hard coding here for speed up
        # h = 360
        # w = 640       
        add = [[image_name,[w,h,all]]]
        dumps += add
    # print(dumps)    
    return dumps
