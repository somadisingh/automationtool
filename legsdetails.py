import cv2
import easyocr
import math
import tqdm
import shutil
import json
import os
import copy
from datetime import datetime


if not os.path.exists('legcrops'):
    os.makedirs('legcrops')

def imgtotxt(img_path): # function to extract text from image
    reader = easyocr.Reader(['en'])
    img = cv2.imread(img_path)
    result = reader.readtext(img)
    text = []
    for i in result:
        text.append(i[1])
    return text, result, img


# if __name__ == '__main__':
#     img_path = 'legdets.png'
#     text, result, img = imgtotxt(img_path)
#     for (bbox, text, prob) in result:
#         (top_left, top_right, bottom_right, bottom_left) = bbox
#         top_left = (int(top_left[0]), int(top_left[1]))
#         bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
#         cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
#         # cv2.putText(img, f"TL:{top_left}, BR:{bottom_right}", (top_left[0], top_left[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
#     cv2.imwrite('legdets_output.png', img)
#     print('Bounding boxes and coordinates drawn on the image and saved as legdets_output.png')


# if __name__ == '__main__':
#     img_path = 'legdets.png'
#     text, result, img = imgtotxt(img_path)
#     # Sort boxes by top left y coordinate
#     result.sort(key=lambda bbox: bbox[0][0][1])
#     for i in range(len(result) - 1):
#         (bbox, text, prob) = result[i]
#         (top_left, top_right, bottom_right, bottom_left) = bbox
#         top_left = (int(top_left[0]), int(top_left[1]))
#         top_right = (int(top_right[0]), int(top_right[1]))
#         bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
#         bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
#         cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
#         cv2.putText(img, f"TL:{top_left}, TR:{top_right}, BR:{bottom_right}, BL:{bottom_left}", (top_left[0], top_left[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
#     cv2.imwrite('legdets_output.png', img)
#     print('Bounding boxes, coordinates, and distances drawn on the image and saved as legdets_output.png')

ocean = {
    "shipmentLegsRow": {
        "carrierName": "MAEU", # this
        "modeofTransportation": "OCEAN",
        "portOfLoading": "CNQDG", # this 
        "portOfDischarge": "USLGB", # this 
        "requestedPickupDate": "20240306", 
        "requestedPickupTime": "00:00:00", 
        "voyageFlightNo": "410N", # this
        "shipmentFromUnlocode": "CNQDG", # this 
        "shipmentToUnlocode": "USLGB", # this 
        "vesselName": "MAERSK SHIVLING", # this 
        "destinationTransitStop": "True",
        "isVisibilityOnly": "True"
    }
}

rail = {
    "shipmentLegsRow": {
        "carrierName": "MAEU", #this
        "modeofTransportation": "RAIL",
        "requestedDeliveryDate": "20240404", 
        "requestedDeliveryTime": "00:00:00", 
        "shipmentFromUnlocode": "USLGB", #this
        "shipmentToUnlocode": "USJOT" #this
    }
}

dray = {
    "shipmentLegsRow": {
        "carrierName": "NMC1-OAK", #this
        "portOfLoading": None,
        "portOfDischarge": None,
        "modeofTransportation": "DRAY",
        "requestedPickupDate": "20240406", 
        "requestedPickupTime": "00:00:00", 
        "shipmentFromUnlocode": "USJOT", #this https://github.com/uncefact/vocab-locode
        "shipmentToUnlocode": "USPNO", #this https://github.com/datasets/un-locode
        "licencePlateNumber": "LPN1"
    }
}


if __name__ == '__main__':
    img_path = 'damu_legs.png'
    text, result, img = imgtotxt(img_path)
    distances = []
    padding = 6
    for i in range(len(result)):
        (bbox, text, prob) = result[i]
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = (int(top_left[0]), int(top_left[1]))
        top_right = (int(top_right[0]), int(top_right[1]))
        bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
        bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
        # cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
        # cv2.putText(img, f"Box:{i+1}", (top_left[0], top_left[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        for j in range(i+1, len(result)):
            next_bbox = result[j][0]
            next_top_left = (int(next_bbox[0][0]), int(next_bbox[0][1]))
            distance = math.sqrt((next_top_left[0] - top_left[0])**2 + (next_top_left[1] - top_left[1])**2)
            distances.append((f"elclidean_distance_box{i+1}_box{j+1}", distance))
            if distance < 63 : #(>46 & <63)
                min_x = int(min(top_left[0], next_top_left[0]) - padding)
                min_y = int(min(top_left[1], next_top_left[1]) - padding)
                max_x = int(max(bottom_right[0], next_bbox[2][0]) + padding)
                max_y = int(max(bottom_right[1], next_bbox[2][1]) + padding)
                # cv2.rectangle(img, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
                crop = img[min_y:max_y, min_x:max_x]
                cv2.imwrite(f'legcrops/crop_{i+1}_{j+1}.png', crop)

    cv2.imwrite('test.png', img)
    # print('Bounding boxes, coordinates, and distances drawn on the image and saved as legdets_output.png')
    # distances.sort(key=lambda x: x[1])
    # for distance in distances:
    #     if distance[1] < 38:
    #         print(f"{distance[0]} = {distance[1]}")

    json_dict = {}
    with open('template.json') as f:
        json_dict = json.load(f)

    leg_dict = {}
    vessel_dict = {}
    
    crops = os.listdir('legcrops')
    for crop in tqdm.tqdm(crops):
        text, result, img = imgtotxt(f'legcrops/{crop}')
        # print(text)
        # leg_dict[text[0]] = text[2] # text[1] is actual/est and text[2] is the planned value
        # since this maps the planned date and time to the leg, a separate case needs to be made
        # for the vessel details
        # if len(text) >= 3:
        if 'Pick Up' in text[0] or 'Rail Departure' in text[0] or 'Vessel Departure' in text[0]:
            # print(text)
            if (len(text) == 3):
                leg_dict[text[2]] = text[0]
            if (len(text) == 2):
                leg_dict[text[1]] = text[0]
  
    
    shutil.rmtree('legcrops')
    # print vessel_dict
    keys_to_remove = [key for key in leg_dict.keys() if 'Planned' not in key]
    for key in keys_to_remove:
        leg_dict.pop(key)

    # if there is no gap after first 11 characters, add a space
    new_leg_dict = {}
    for key in leg_dict.keys():
        if key[11] != ' ':
            new_key = key[:11] + ' ' + key[11:]
        else:
            new_key = key
        new_leg_dict[new_key] = leg_dict[key]

    leg_dict = new_leg_dict

    sorted_keys = sorted(leg_dict.keys(), key=lambda date: datetime.strptime(date.split(' ')[0], '%d-%b-%Y'))
    # replace the keys in leg_dict with sorted keys
    leg_dict = dict((key, leg_dict[key]) for key in sorted_keys)

    for key in leg_dict.keys():
        print(f"{key}: {leg_dict[key]}")
        

    shipmentLegs = []
    for key in leg_dict.keys():
        # print(f"{key}: {leg_dict[key]}")
        # date & time extraction
        if 'Rail Departure' in leg_dict[key] or 'Vessel Departure' in leg_dict[key] or 'Pick Up' in leg_dict[key]:
            # print(f"{key}: {leg_dict[key]}")
            mainkey = key
            # extract date and time separately
            datekey = mainkey.split(' ')[0]
            timekey = mainkey.split(' ')[1]

            # datekey preprocessing
            datekey = datekey.split('-')
            month = datekey[1]
            day = datekey[0]
            year = datekey[2]
            if month == 'Jan':
                month = '01'
            elif month == 'Feb':
                month = '02'
            elif month == 'Mar':
                month = '03'
            elif month == 'Apr':
                month = '04'
            elif month == 'May':
                month = '05'
            elif month == 'Jun':
                month = '06'
            elif month == 'Jul':
                month = '07'
            elif month == 'Aug':
                month = '08'
            elif month == 'Sep':
                month = '09'
            elif month == 'Oct':
                month = '10'
            elif month == 'Nov':
                month = '11'
            elif month == 'Dec':
                month = '12'
            datekey = year + month + day
            
            # timekey preprocessing
            timekey = timekey + ':00'
            timekey = timekey.replace('.', ':')
        
        if 'Vessel Departure' in leg_dict[key]:
            # print(leg_dict[key])
            ocean_copy = copy.deepcopy(ocean)
            ocean_copy['shipmentLegsRow']['requestedPickupDate'] = datekey
            ocean_copy['shipmentLegsRow']['requestedPickupTime'] = timekey
            shipmentLegs.append(ocean_copy)
            # print(ocean_copy)
        if 'Rail Departure' in leg_dict[key]:
            # print(leg_dict[key])
            rail_copy = copy.deepcopy(rail)
            rail_copy['shipmentLegsRow']['requestedDeliveryDate'] = datekey
            rail_copy['shipmentLegsRow']['requestedDeliveryTime'] = timekey
            shipmentLegs.append(rail_copy)
            # print(rail_copy)
        if 'Pick Up' in leg_dict[key]:
            # print(leg_dict[key])
            dray_copy = copy.deepcopy(dray)
            dray_copy['shipmentLegsRow']['requestedPickupDate'] = datekey
            dray_copy['shipmentLegsRow']['requestedPickupTime'] = timekey
            shipmentLegs.append(dray_copy)
            # print(dray_copy)

    # print(shipmentLegs)
    json_dict['event']['shipmentLegs'] = shipmentLegs
    jsonname = datetime.now().strftime("%Y%m%d%H%M%S") + '.json'
    with open(jsonname, 'w') as f:
        json.dump(json_dict, f, indent=4)
    print(f"JSON file {jsonname} created successfully")
    

# TODO: unlocodes, carrier names, vessel names, and voyage numbers need to be extracted from the image