from PIL import Image
import requests
from io import BytesIO
import numpy as np
from random import random
import argparse
import sys

parser = argparse.ArgumentParser(description='Minimal example of dumping args into log file.')
parser.add_argument('--img_url',type=str, default="https://source.unsplash.com/iXp4yp8A9Tw/1920x1306",
                    help='Horizontal step length')
parser.add_argument('--h_len',type=int, default=5,
                    help='Horizontal step length')
parser.add_argument('--v_len',type=int, default=5,
                    help='Vertical step length')


args = parser.parse_args()


class Canvas:
    def __init__(self, img):
        self.img = img
        self.imgs = [img]

    def generate(self, h_splits, v_splits, thresh = .5):
        res = self.imgs[-1].copy()
        res.setflags(write=1)
        height, width, _ = res.shape
        h_step_size = width//h_splits
        v_step_size = height//v_splits
        

        for i in range(h_splits):
            if random() > thresh:
                continue
            for j in range(v_splits):
                if random() > thresh:
                    continue
                h_s = np.random.randint(h_step_size//2, h_step_size)
                v_s = np.random.randint(v_step_size//2, v_step_size)
                start_h, end_h = h_s*i, h_s*(i+1)
                start_v, end_v = v_s*j, v_s*(j+1)
                sub_img = self.img[start_v:end_v,start_h:end_h,:]
                modified_img = np.ones_like(sub_img)*np.median(sub_img, axis = [0,1])
                res[start_v:end_v,start_h:end_h,:] = modified_img        

        res_im = Image.fromarray(np.uint8(res))

        self.imgs.append(np.asarray(res_im))

        return res_im


    def undo(self):
        _ = self.imgs.pop()

        return Image.fromarray(np.uint8(self.imgs[-1]))


if __name__ == "__main__":
    url = args.img_url
    h_len, v_len = args.h_len, args.v_len
    response = requests.get(url)
    try:
        img = Image.open(BytesIO(response.content))
    except:
        print("Bad URL")
        sys.exit()

    geometric_img = Canvas(np.asarray(img))
    res_im = geometric_img.generate(h_splits=h_len, v_splits=v_len, thresh=.9)
    res_im.save("outpout" + "." + img.format)