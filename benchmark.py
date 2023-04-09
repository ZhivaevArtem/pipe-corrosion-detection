from json import load
import sys
import time
import numpy as np
import torch
from torchvision.transforms.functional import to_tensor
from cv2 import resize

from Data import ImageIO
from Training_functions import pixel_accuracy, mIoU
from Simple_Unet import *

data = None
with open(sys.argv[1],'rb') as file:
    data = file.read()
img_io = ImageIO()
img = img_io.load(data)
mask = np.load(sys.argv[2])
shape = img_io.w,img_io.h
mask = resize(mask,shape)
mask = to_tensor(mask)
model = UNet(num_class=7)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.load_state_dict(torch.load('dict.pth', map_location=device))
model.eval()
start = time.perf_counter()
res = model(img)
end = time.perf_counter()
acc = pixel_accuracy(res,mask)
iou = mIoU(res,mask,7)
print('Accuracy: {}, IoU: {}, time elapsed: {}'.format(acc,iou,end-start))
