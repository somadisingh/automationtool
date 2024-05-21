# import cv2
# import easyocr

# pip install easyocr, opencv-python, numpy, torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# def imgtotxt(img_path): # function to extract text from image
#     reader = easyocr.Reader(['en'])
#     img = cv2.imread(img_path)
#     result = reader.readtext(img)
#     text = []
#     for i in result:
#         text.append(i[1])
#     return text

# if __name__ == '__main__':
#     img_path = 'basic.png'
#     text = imgtotxt(img_path)
#     for i in text:
#         if i.isupper():
#             print(i)
#             break


# if __name__ == '__main__':
#     img_path = 'basic.png'
#     text, result, img = imgtotxt(img_path)
#     for (bbox, text, prob) in result:
#         (top_left, top_right, bottom_right, bottom_left) = bbox
#         top_left = (int(top_left[0]), int(top_left[1]))
#         bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
#         cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
#         cv2.putText(img, f"TL:{top_left}, BR:{bottom_right}", (top_left[0], top_left[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
#     cv2.imwrite('basic_output.png', img)
#     print('Bounding boxes and coordinates drawn on the image and saved as basic_output.png')


# if __name__ == '__main__':
#     img_path = 'basic.png'
#     text, result, img = imgtotxt(img_path)
#     # Sort boxes by top left y coordinate
#     result.sort(key=lambda bbox: bbox[0][0][1])
#     for i in range(len(result) - 1):
#         (bbox, text, prob) = result[i]
#         (top_left, top_right, bottom_right, bottom_left) = bbox
#         top_left = (int(top_left[0]), int(top_left[1]))
#         bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
#         cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
#         cv2.putText(img, f"TL:{top_left}, BR:{bottom_right}", (top_left[0], top_left[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
#         # Calculate vertical distance to next box
#         next_bbox = result[i + 1][0]
#         next_top_left = (int(next_bbox[0][0]), int(next_bbox[0][1]))
#         distance = next_top_left[1] - bottom_right[1]
#         # Draw distance in the middle of the two boxes
#         cv2.putText(img, f"D:{distance}", (top_left[0], bottom_right[1] + distance // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
#     cv2.imwrite('basic_output.png', img)
#     print('Bounding boxes, coordinates, and distances drawn on the image and saved as basic_output.png')


# if __name__ == '__main__':
#     img_path = 'basic.png'
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
#     cv2.imwrite('basic_output.png', img)
#     print('Bounding boxes, coordinates, and distances drawn on the image and saved as basic_output.png')



# if __name__ == '__main__':
#     img_path = 'basic.png'
#     text, result, img = imgtotxt(img_path)
#     # Sort boxes by top left y coordinate
#     result.sort(key=lambda bbox: bbox[0][0][1])
#     distances = []
#     for i in range(len(result)):
#         (bbox, text, prob) = result[i]
#         (top_left, top_right, bottom_right, bottom_left) = bbox
#         top_left = (int(top_left[0]), int(top_left[1]))
#         top_right = (int(top_right[0]), int(top_right[1]))
#         bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
#         bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
#         cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
#         # cv2.putText(img, f"TL:{top_left}, TR:{top_right}, BR:{bottom_right}, BL:{bottom_left}", (top_left[0], top_left[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
#         cv2.putText(img, f"Box:{i+1}", (top_left[0], top_left[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
#         for j in range(i+1, len(result)):
#             next_bbox = result[j][0]
#             next_top_left = (int(next_bbox[0][0]), int(next_bbox[0][1]))
#             distance = math.sqrt((next_top_left[0] - top_left[0])**2 + (next_top_left[1] - top_left[1])**2)
#             distances.append((f"elclidean_distance_box{i+1}_box{j+1}", distance))
#     cv2.imwrite('basic_output1.png', img)
#     print('Bounding boxes, coordinates, and distances drawn on the image and saved as basic_output.png')
#     distances.sort(key=lambda x: x[1])
#     for distance in distances:
#         print(f"{distance[0]} = {distance[1]}")

import cv2
import easyocr
import math
import tqdm
import shutil
import json
import datetime
import os


if not os.path.exists('refcrops'):
    os.makedirs('refcrops')

def imgtotxt(img_path): # function to extract text from image
    reader = easyocr.Reader(['en'])
    img = cv2.imread(img_path)
    result = reader.readtext(img)
    text = []
    for i in result:
        text.append(i[1])
    return text, result, img


if __name__ == '__main__':
    img_path = 'cargoquiktest.png'
    text, result, img = imgtotxt(img_path)
    # Sort boxes by top left y coordinate
    result.sort(key=lambda bbox: bbox[0][0][1])
    distances = []
    padding = 4
    for i in range(len(result)):
        (bbox, text, prob) = result[i]
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = (int(top_left[0]), int(top_left[1]))
        top_right = (int(top_right[0]), int(top_right[1]))
        bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
        bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
        for j in range(i+1, len(result)):
            next_bbox = result[j][0]
            next_top_left = (int(next_bbox[0][0]), int(next_bbox[0][1]))
            distance = math.sqrt((next_top_left[0] - top_left[0])**2 + (next_top_left[1] - top_left[1])**2)
            distances.append((f"euclidean_distance_box{i+1}_box{j+1}", distance))
            if distance < 52:
                min_x = min(top_left[0], next_top_left[0]) - padding
                min_y = min(top_left[1], next_top_left[1]) - padding
                max_x = max(bottom_right[0], next_bbox[2][0]) + padding
                max_y = max(bottom_right[1], next_bbox[2][1]) + padding
                cv2.rectangle(img, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
                crop = img[min_y:max_y, min_x:max_x]
                cv2.imwrite(f'refcrops/crop_{i+1}_{j+1}.png', crop)
                
    cv2.imwrite('basic_outputoftesting1.png', img)
    
    
    json_dict = {}
    with open('template.json') as f:
        json_dict = json.load(f)

    text_dict = {}
    
    crops = os.listdir('refcrops')
    for crop in tqdm.tqdm(crops):
        text, result, img = imgtotxt(f'refcrops/{crop}')
        if len(text) > 1:
            text_dict[text[0]] = text[1]
    
    shutil.rmtree('refcrops')

    serial = 1
    for key in text_dict.keys():
        print(f"{serial}: {key}: {text_dict[key]}")
        serial += 1
    serial_numbers = input("Enter serial numbers to update JSON values: ")
    serial_numbers = serial_numbers.split(',')
    # remove out of range serial numbers and remove duplicates and any other characters
    serial_numbers = list(set([i for i in serial_numbers if i.isnumeric() and int(i) <= len(text_dict)]))
    for serial_number in tqdm.tqdm(serial_numbers):
        # print(f"{list(text_dict.keys())[int(serial_number)-1]}: {list(text_dict.values())[int(serial_number)-1]}")
        keys = list(text_dict.keys())[int(serial_number)-1]
        for key in keys.split(','):
            if key == 'Master Bill of Lading':
                json_dict['event']['header']['headerRow']['shipmentReferenceBillOfLadding'] = text_dict['Master Bill of Lading']
            elif key == 'Container ID':
                json_dict['event']['equipment'][0]['equipmentRow']['shipmentEquipmentNumber'] = text_dict['Container ID']
            elif key == 'Service Type':
                json_dict['event']['header']['headerRow']['serviceType'] = text_dict['Service Type']
            elif key == 'CutOff Date':
                json_dict['event']['header']['headerRow']['cutOffDate'] = text_dict['CutOff Date']
            elif key == 'Cargo Ready Date':
                json_dict['event']['header']['headerRow']['cargoReadyDate'] = text_dict['Cargo Ready Date']
    
    now = datetime.datetime.now()
    date_time = now.strftime("%d%m%Y%H%M")
    shipmentReferenceNumber = f"QAPE{date_time}"
    shipmentReferenceMasterWayBill = f"MWB{date_time}"
    shipmentReferenceHouseWayBill = f"HWB{date_time}"
    json_dict['event']['header']['headerRow']['shipmentReferenceNumber'] = shipmentReferenceNumber
    json_dict['event']['header']['headerRow']['shipmentReferenceMasterWayBill'] = shipmentReferenceMasterWayBill
    json_dict['event']['header']['headerRow']['shipmentReferenceHouseWayBill'] = shipmentReferenceHouseWayBill
    # json_dict['event']['header']['headerRow']['cargoReadyDate'] = None
    # json_dict['event']['header']['headerRow']['cutOffDate'] = None
    
    with open('pae_updated.json', 'w') as f:
        json.dump(json_dict, f, indent=4)

    print("JSON updated successfully!")
