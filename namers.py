import cv2
import easyocr
import math
import tqdm
import shutil
import json
import os
import copy
from datetime import datetime

# if not os.path.exists('namercrops'):
#     os.makedirs('namercrops')

def imgtotxt(img_path): # function to extract text from image
    reader = easyocr.Reader(['en'])
    img = cv2.imread(img_path)
    result = reader.readtext(img)
    text = []
    for i in result:
        text.append(i[1])
    # print(text)
    return text, result, img
# list = ['Planned']
list = ['Planned', 'Actual', 'Est', 'Arrival', 'Gate', 'Rail', 'Load', 'Unload', 'Available', 'Vessel', 'Delivered', 'Customs', 'Pick', 'Jan', 'Feb', 'Apr', 'May', 'Jun', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'View', 'Milestone', 'Event', 'ETT', 'ATT']
filtered_result = []

def primaryfilter():
    img_path = 'damu_legs.png'
    text, result, img = imgtotxt(img_path)
    for (bbox, text, prob) in tqdm.tqdm(result):
        # if the text in list is not found in the text extracted from the image and text not number
        if not any(word in text for word in list) and not text.isnumeric():
            filtered_result.append((bbox, text, prob))
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = (int(top_left[0]), int(top_left[1]))
            bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
            cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
        # cv2.putText(img, f"TL:{top_left}, BR:{bottom_right}", (top_left[0], top_left[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    cv2.imwrite('damu_name_testing.png', img)
    print('Bounding boxes and coordinates drawn on the image and saved as damu_name_testing.png')
    # print(filtered_result)
    return filtered_result

def boxjoiner():
    # img_path = 'damu_legs.png'
    # text, result, img = imgtotxt(img_path)
    filtered_result=primaryfilter()
    distances = []
    padding = 3
    img = cv2.imread('damu_legs.png')
    for i in range(len(filtered_result)):
        (bbox, text, prob) = filtered_result[i]
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = (int(top_left[0]), int(top_left[1]))
        top_right = (int(top_right[0]), int(top_right[1]))
        bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
        bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
        # cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
        # cv2.putText(img, f"Box:{i+1}", (top_left[0], top_left[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        for j in range(i+1, len(filtered_result)):
            next_bbox = filtered_result[j][0]
            next_top_left = (int(next_bbox[0][0]), int(next_bbox[0][1]))
            distance = math.sqrt((next_top_left[0] - top_left[0])**2 + (next_top_left[1] - top_left[1])**2)
            distances.append((f"elclidean_distance_box{i+1}_box{j+1}", distance))
            if distance < 63 : #(>46 & <63)
                min_x = int(min(top_left[0], next_top_left[0]) - padding)
                min_y = int(min(top_left[1], next_top_left[1]) - padding)
                max_x = int(max(bottom_right[0], next_bbox[2][0]) + padding)
                max_y = int(max(bottom_right[1], next_bbox[2][1]) + padding)
                cv2.rectangle(img, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
                # crop = img[min_y:max_y, min_x:max_x]
    cv2.imwrite('namerseuclid.png', img)
    print('Bounding boxes, coordinates, and distances drawn on the image and saved as namerseuclid.png')
    distances.sort(key=lambda x: x[1])
    # for distance in distances:
        # if distance[1] < 38:
        # print(f"{distance[0]} = {distance[1]}")






if __name__ == '__main__':
    # primaryfilter()
    boxjoiner()

