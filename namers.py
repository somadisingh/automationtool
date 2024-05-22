import cv2
import easyocr
import math
import tqdm
import shutil
import json
import os
import copy
from datetime import datetime
import pandas as pd

if not os.path.exists('namercrops'):
    os.makedirs('namercrops')

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
locations = []
unlocodes = []

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

def boxjoinerfilter():
    # img_path = 'damu_legs.png'
    # text, result, img = imgtotxt(img_path)
    filtered_result=primaryfilter()
    # distances = []
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
            # distances.append((f"elclidean_distance_box{i+1}_box{j+1}", distance))
            if distance < 63 : #(>46 & <63)
                min_x = int(min(top_left[0], next_top_left[0]) - padding)
                min_y = int(min(top_left[1], next_top_left[1]) - padding)
                max_x = int(max(bottom_right[0], next_bbox[2][0]) + padding)
                max_y = int(max(bottom_right[1], next_bbox[2][1]) + padding)
                # cv2.rectangle(img, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
                # number the boxes
                # cv2.putText(img, f"Box:{i+1}", (top_left[0], top_left[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                crop = img[min_y:max_y, min_x:max_x]
                cv2.imwrite(f'namercrops/crop_{i+1}_{j+1}.png', crop)
    # cv2.imwrite('namerseuclid.png', img)
    print('Bounding boxes, coordinates, and distances drawn on the image and saved as namerseuclid.png')
    # distances.sort(key=lambda x: x[1])
    # for distance in distances:
        # if distance[1] < 38:
        # print(f"{distance[0]} = {distance[1]}")
    # crops = os.listdir('namercrops')
    # for crop in tqdm.tqdm(crops):
        # text, result, img = imgtotxt(f'namercrops/{crop}')
        #PREPROCESSING NEEDS TO BE DONE HERE
        # locations.append((text))
        # print(f'{crop} : {text}')
    # print(locations)


def locationextractor():
    crops = os.listdir('namercrops')
    for crop in tqdm.tqdm(crops):
        text, result, img = imgtotxt(f'namercrops/{crop}')
        #PREPROCESSING NEEDS TO BE DONE HERE
        text = [x.replace(";", ",") for x in text] # replacing ; with ,
        # iterate through the text array and check if any of the text contains a ,
        new_text = []
        for i in range(len(text)):
            if ',' in text[i]:
                # remove all other text except the text containing ,
                new_text.append(text[i])
            if '_' in text[i]:
                # remove this text
                text[i] = ''
        if len(new_text) > 0 : text = new_text
        locations.append((text))
        # print(f'{crop} : {text}')
    # print(locations)
    return locations


def unlocodeextractor():
    locations = locationextractor()
    print(locations)
    # read csv file
    df = pd.read_csv('unlocode.csv')
    # drop the columns Changed, Name, Remarks, Coordinates, Date, Function, Status
    df = df.drop(['Change', 'Name', 'Remarks', 'Coordinates', 'Date', 'Function', 'Status', 'IATA'], axis=1)
    # print(df)
    # iterate through the df and check if the Subdivision cell is not empty, it not empty then add it to the NameWoDiacritics column in the format of NameWoDiacritics, Subdivision
    for index, row in df.iterrows():
        if not pd.isnull(row['Subdivision']):
            df.at[index, 'NameWoDiacritics'] = row['NameWoDiacritics'] + ', ' + row['Subdivision']
    # iterate through the locations
    for location in locations:
        # print(location)
        for loc in location:
            print(loc)
            # check if the location is present in the NameWoDiacritics column. match exact string
            # if loc contains a , (example format Los Angeles, CA)
            if ',' in loc:
                if loc in df['NameWoDiacritics'].values:
                    print(df[df['NameWoDiacritics'] == loc])
                    # if present then combine values in Country and Location column together one as a string
                    unlocode = df[df['NameWoDiacritics'] == loc]['Country'].values[0] + df[df['NameWoDiacritics'] == loc]['Location'].values[0]
                    print(unlocode)
                    # check if value is not already present in the unlocodes list, then add it
                    if unlocode not in unlocodes:
                        unlocodes.append(unlocode)
            elif len(loc) > 0:
                if df['NameWoDiacritics'].str.contains(loc, na=False).any():
                    print(df[df['NameWoDiacritics'].str.contains(loc, na=False)])
                    # if present then combine values in Country and Location column together one as a string
                    unlocode = df[df['NameWoDiacritics'].str.contains(loc, na=False)]['Country'].values[0] + df[df['NameWoDiacritics'].str.contains(loc, na=False)]['Location'].values[0]
                    print(unlocode)
                    # check if value is not already present in the unlocodes list, then add it
                    if unlocode not in unlocodes:
                        unlocodes.append(unlocode)
    print(unlocodes)
    return unlocodes             




if __name__ == '__main__':
    # primaryfilter()
    boxjoinerfilter()
    # locationextractor()
    unlocodeextractor()

