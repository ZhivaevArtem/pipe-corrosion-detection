#Загрузка и предобработка информации

import numpy as np
import pandas as pd
import os
import io
import cv2

import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms as T

from PIL import Image


def get_names(IMG_PATH):
    names = []
    for _,_,files in os.walk(IMG_PATH):
        for file in files:
            names.append(file.split('.')[0])
    return pd.DataFrame({'id':names}, index = np.arange(len(names)))
    
    
class ImageIO:
    def load(self,bytes):
        img_arr = np.frombuffer(bytes,np.uint8)
        img = cv2.imdecode(img_arr,cv2.IMREAD_COLOR)
        cv2.imwrite('static/temp/image.jpg',img)
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        self.h,self.w,_ = img.shape
        h_mod = (self.h//16)*16
        w_mod = (self.w//16)*16
        if (h_mod != self.h) or (w_mod != self.w):
            img = cv2.resize(img,(w_mod,h_mod))
        mean=[0.485, 0.456, 0.406] #Эти числа всё время встречаются в документации PyTorch
        std=[0.229, 0.224, 0.225] #Поэтому использованы именно они
        t = T.Compose([T.ToTensor(),T.Normalize(mean,std)])
        img = t(img)
        sh = img.shape
        img = img.reshape(1,sh[0],sh[1],sh[2])
        return img

    def save(self,img,path):
        suffix = '.png'
        percents = []
        nc = img.shape[1]
        img = torch.argmax(F.softmax(img, dim=1), dim=1)
        sh = img.shape
        img = img.detach().cpu().numpy().reshape((sh[1],sh[2]))
        img = np.uint8(img)
        img = cv2.resize(img,(self.w,self.h))
        b=np.empty_like(img)
        g=np.empty_like(img)
        r=np.empty_like(img)
        size = sh[1]*sh[2]
        for i in range(nc):
            mask = np.full_like(img,i)
            layer = np.array(img==mask,np.uint8)
            layer_b = np.zeros_like(img)
            layer_g = np.zeros_like(img)
            layer_r = np.zeros_like(img)
            layer_a = np.array(layer)
            if(i%2):
                layer_b[:,:] = layer[:,:]
                b += layer
            if((i//2)%2):
                g += layer
                layer_g[:,:] = layer[:,:]
            if((i//4)%2):
                r += layer
                layer_r[:,:] = layer[:,:]
            percent = int(np.count_nonzero(layer)/size*100)
            percents.append(percent)
            layer = cv2.merge((layer_b,layer_g,layer_r,layer_a))
            _,layer = cv2.threshold(layer,0,255,cv2.THRESH_BINARY)
            cv2.imwrite(f'{path}_layer{i}{suffix}',layer)
        img = cv2.merge((b,g,r))
        _,img = cv2.threshold(img,0,255,cv2.THRESH_BINARY)
        cv2.imwrite(f'{path}{suffix}',img)
        return percents  
        
        
class PipeDataset(Dataset):
    def __init__(self,img_path,mask_path, sample_ids,transform=None):
        self.img_path = img_path
        self.mask_path = mask_path
        self.sample_ids = sample_ids
        self.transform = transform
        
    def __len__(self):
        return len(self.sample_ids)
        
    def __getitem__(self,idx):
        img = Image.open(self.img_path+self.sample_ids[idx]+'.png')
        mask = np.load(self.mask_path+self.sample_ids[idx]+'.npy')
        if self.transform is not None:
            img = np.array(img)
            aug = self.transform(image=img,mask=mask)
            img = aug['image']
            mask = aug['mask']
        mean=[0.485, 0.456, 0.406] #Эти числа всё время встречаются в документации PyTorch
        std=[0.229, 0.224, 0.225] #Поэтому использованы именно они
        t = T.Compose([T.ToTensor(),T.Normalize(mean,std)])
        img = t(img)
        mask = torch.from_numpy(mask).long()
        
        return img,mask


    
