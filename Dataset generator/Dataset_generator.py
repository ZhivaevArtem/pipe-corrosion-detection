import os
import random
import numpy as np
import cv2
from PIL import Image
import sys
import json

'''
This script makes dataset generation a bit easier.

'''

def trim_json(path):
    file_i = open(path,'r',encoding='utf-8')
    data_i = json.load(file_i)
    file_i.close()
    data_o = {'shapes':data_i['shapes'], 'width':data_i['imageWidth'], 'height':data_i['imageHeight']}
    defects = data_o['shapes']
    for d in defects:
        for i in range(len(d['points'])):
            for j in range(2):
                d['points'][i][j] = int(d['points'][i][j])
        tmp = sorted(d['points'],key=lambda x: x[0])
        d['x0'] = tmp[0][0]
        d['width'] = tmp[-1][0] - d['x0']
        tmp = sorted(d['points'],key=lambda x: x[1])
        d['y0'] = tmp[0][1]
        d['height'] = tmp[-1][1] - d['y0']
        for i in range(len(d['points'])):
            d['points'][i][0] -= d['x0']
            d['points'][i][1] -= d['y0']
    file_o = open(path,'w',encoding='utf-8')
    json.dump(data_o,file_o,ensure_ascii=False)
    file_o.close()


def generate_defect_regions(path):
    names = set([file.split('.')[0] for file in os.listdir(path)])
    os.mkdir(f'{path}\\images')
    os.mkdir(f'{path}\\masks')
    descriptions = {'засоленность': [1,0], 'коррозия по телу': [2,0], \
                    'питтинг': [3,0], 'слой нефтепродуктов': [4,0], \
                    'углубление': [5,0], 'углубление протяженное': [6,0]}
    for i in names:
        data = None
        with open(f'{path}\\{i}.json',encoding='utf-8') as file:
            data = json.load(file)['shapes']
        img = cv2.imread(f'{path}\\{i}.jpg')
        for d in data:
            x0,y0 = d['x0'],d['y0']
            w,h = d['width'],d['height']
            def_type,num = descriptions[d['label']]
            roi = img[y0:y0+h,x0:x0+w]
            poly = np.array(d['points']).reshape(1,len(d['points']),2)
            d_mask = np.zeros((h,w),np.uint8)
            label_mask = np.zeros((h,w),np.uint8)
            cv2.fillPoly(d_mask,poly,255)
            cv2.fillPoly(label_mask,poly,descriptions[d['label']][0])
            roi = cv2.bitwise_and(roi,roi,mask=d_mask)
            cv2.imwrite(f'{path}\\images\\{def_type}_{num}.png',roi)
            np.save(f'{path}\\masks\\{def_type}_{num}.npy',label_mask)
            descriptions[d['label']][1] += 1


def generate_samples(path,sample_num,def_num):
    names = [name.split('.')[0] for name in os.listdir(f'{path}\\images')]
    os.mkdir(f'{path}\\data\\images')
    os.mkdir(f'{path}\\data\\masks')
    for i in range(sample_num):
        canvas = cv2.imread(f'{path}\\canvas.png')
        h,w,c = canvas.shape
        mask = np.zeros((h,w),np.uint8)
        for j in range(def_num):
            name = random.choice(names)
            d_img = cv2.imread(f'{path}\\images\\{name}.png')
            d_mask = np.load(f'{path}\\masks\\{name}.npy')
            _,d_mask_img = cv2.threshold(d_mask,0,255, cv2.THRESH_BINARY)
            d_mask_inv = cv2.bitwise_not(d_mask_img)
            d_h,d_w,_ = d_img.shape
            x0,y0 = random.randrange(w-d_w),random.randrange(h-d_h)

            roi = canvas[y0:y0+d_h,x0:x0+d_w]
            d_img = cv2.bitwise_and(d_img,d_img,mask=d_mask_img)
            roi = cv2.bitwise_and(roi,roi,mask=d_mask_inv)
            roi += d_img
            canvas[y0:y0+d_h,x0:x0+d_w] = roi

            roi = mask[y0:y0+d_h,x0:x0+d_w]
            d_mask = cv2.bitwise_and(d_mask,d_mask,mask=d_mask_img)
            roi = cv2.bitwise_and(roi,roi,mask=d_mask_inv)
            roi += d_mask
            mask[y0:y0+d_h,x0:x0+d_w] = roi
        cv2.imwrite(f'{path}\\data\\images\\{i}.png',canvas)
        np.save(f'{path}\\data\\masks\\{i}.npy',mask)


if __name__ == '__main__':
    generate_samples(sys.argv[0],int(sys.argv[1]),int(sys.argv[2]))


# WIP
# def generate_samples_complex(number: int,defects: dict):
#     for i in range(number):
#         canvas = cv2.imread('.\\Dataset generator\\canvas.png')
#         h,w,c = canvas.shape
#         mask = np.zeros((h,w),np.uint8)
#         for d_id in defects:
#             for j in range(defects[d_id]):
#                 d = random.randrange(labels[d_id])
#                 d_img = cv2.imread(f'.\\Dataset generator\\images\\{d_id}_{d}.png')
#                 d_mask = np.load(f'.\\Dataset generator\\masks\\{d_id}_{d}.npy')
#                 _,d_mask_img = cv2.threshold(d_mask,0,255, cv2.THRESH_BINARY)
#                 d_mask_inv = cv2.bitwise_not(d_mask_img)
#                 d_h,d_w,_ = d_img.shape
#                 x0,y0 = random.randrange(w-d_w),random.randrange(h-d_h)

#                 roi = canvas[y0:y0+d_h,x0:x0+d_w]
#                 d_img = cv2.bitwise_and(d_img,d_img,mask=d_mask_img)
#                 roi = cv2.bitwise_and(roi,roi,mask=d_mask_inv)
#                 roi += d_img
#                 canvas[y0:y0+d_h,x0:x0+d_w] = roi

#                 roi = mask[y0:y0+d_h,x0:x0+d_w]
#                 d_mask = cv2.bitwise_and(d_mask,d_mask,mask=d_mask_img)
#                 roi = cv2.bitwise_and(roi,roi,mask=d_mask_inv)
#                 roi += d_mask
#                 mask[y0:y0+d_h,x0:x0+d_w] = roi
#         cv2.imwrite(f'.\\Dataset generator\\data\\images\\{i}.png',canvas)
#         np.save(f'.\\Dataset generator\\data\\masks\\{i}.npy',mask)