from torch.utils.data import Dataset, DataLoader
from ingradient_library.transform import Transform
from ingradient_library.preprocessing import *
from ingradient_library.get_nnunet_setting import *
from ingradient_library.patch_transform import *
from ingradient_library.unet import *
import torch.nn as nn
import torch.nn.functional as F
import torch
import numpy as np
import os
import h5py
import copy
import numpy as np
import cc3d


class MAIC_Dataset(Dataset):
    def __init__(self, path = None, normalizer = True, train = True, transform = Transform(*get_maic_params(None))):
        if path == None:
            path = '../mnt/dataset/'
        
        self.path = path
        self.file_list = []
        for f in os.listdir(path):
            if not 'py' in f:
                self.file_list.append(f)
        
        self.file_list = sorted(self.file_list)
        self.normalizer = normalizer
        self.train = train
        self.sampler = MAIC_Sampling(transform = transform, train = train)
        self.norm1 = Fixed_Normalizer(mean = 20.78, std = 180.50, min = -986, max = 271,  device = None)
        #self.norm1 = Fixed_Normalizer(mean = -410, std = 400,  device = None)
        
    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, idx):
        current_file = os.path.join(self.path, self.file_list[idx])
        hdf_file = h5py.File(current_file , 'r')
        CT = np.array(hdf_file['CT'])
        PET = np.array(hdf_file['PET'])
        spacing = np.array(hdf_file['Size'])
        
        if self.train:
            seg = np.array(hdf_file['Aorta'])
            images = np.expand_dims(CT ,axis = 0)
        
        else:
            images = np.stack((CT, PET))
            seg = None
        
        hdf_file.close()
        images, seg = self.sampler(images, seg)
        if self.normalizer:
            images[0] = self.norm1(images[0])
        
        if not self.train:
            PET = images[1]
            images = np.expand_dims(images[0], axis = 0)
            return images, seg, spacing, PET
        else:
            return images, seg, spacing, 1
        
class CT_Lung_Cropping(object):
    def __init__(self, clip = False, threshold_clip = [-900, -200 ], threshold_cut = [-1000, -350]):
        self.clip = clip
        self.threshold_clip = threshold_clip
        self.threshold_cut = threshold_cut
    
    def __call__(self, image):
        if self.clip:
            clip_img = np.clip(image, self.threshold_clip[0], self.threshold_clip[1])
        else:
            clip_img = image
        mask =  (clip_img > self.threshold_cut[0]) * (clip_img < self.threshold_cut[1])
        if not isinstance(mask, np.ndarray):
            mask = mask.numpy()
        conected_component_mask = cc3d.connected_components(mask, connectivity = 26)
        count = np.unique(conected_component_mask, return_counts = True)[1]
        lung_index = np.argsort(count)[::-1]
        if len(lung_index) > 2:
            lung_index = lung_index[2]
        
        else:
            lung_index = lung_index[-1]
        lung_max = np.max(np.where(conected_component_mask == lung_index), axis = 1)
        lung_min = np.min(np.where(conected_component_mask == lung_index), axis = 1)
        
        return lung_min, lung_max


class MAIC_Sampling(object):
    def __init__(self,  train = True, transform = None):
        self.transform = transform
        self.train = train
        self.lung_cut = CT_Lung_Cropping()
        
    def __call__(self, images, seg = None, is_CT = True):
        if not isinstance(images, np.ndarray):
            images = np.array(images)
            if self.train:
                seg = np.array(seg)
        
        
        temp = copy.deepcopy(images)
        if is_CT:
            temp[np.where(temp < - 700)] = 0
        
        non_zero_index = np.where(temp.astype(int) != 0)
        min_val = np.min(non_zero_index, axis = 1)
        max_val = np.max(non_zero_index, axis = 1)
        if self.train:
            random_move = np.random.randint([-5,-5,-5], [5, 5, 5])
        else:
            random_move = np.array([0,0,0])
        random_move = np.array([0,0,0])
        images = images[:, min_val[-3]:max_val[-3]+1, min_val[-2]:max_val[-2]+1, min_val[-1]:max_val[-1]+1]
        z_start = int(images.shape[-1] * 0.25)
        z_term = 128
        y_start = images.shape[-2]//2 - 40
        y_end= images.shape[-2]//2 + 40
        x_term = 128
        images = images[:, 5 + random_move[0]:x_term+random_move[0]+5, y_start+random_move[1]:y_end+random_move[1],
                       -(z_start + z_term) + random_move[2]:-z_start + random_move[2]]
        
        lung_index = self.lung_cut(images[0])
        lung_center = (lung_index[0] + lung_index[1])//2
        lung_center[2] = min(lung_center[2], 128 - 48)
        images = images[:, lung_center[0]-24:lung_center[0]+24, lung_center[1] - 24: lung_center[1] + 24, lung_center[2]-48:lung_center[2]+48]
        if self.train:
            seg = seg[min_val[-3]:max_val[-3]+1, min_val[-2]:max_val[-2]+1, min_val[-1]:max_val[-1]+1]
            seg = seg[5 + random_move[0]:x_term+random_move[0]+5, y_start+random_move[1]:y_end+random_move[1],
                       -(z_start + z_term) + random_move[2]:-z_start + random_move[2]]
            seg = seg[lung_center[0]-24:lung_center[0]+24, lung_center[1] - 24: lung_center[1] + 24, lung_center[2]-48:lung_center[2]+48]
            images = torch.tensor(images).unsqueeze(0).double()
            seg = torch.tensor(seg).unsqueeze(0).long()
            if self.transform != None:
                images, seg = self.transform(images, seg, None)
            images = images.squeeze(0).numpy()
            seg = seg.squeeze(0).numpy()
        else: 
            seg = None

        return images, seg


class MU_Dataset(Dataset):
    def __init__(self, path = None, normalizer = True, train = True, transform = None):
        if path == None:
            path = '../mnt/dataset/'
        
        self.path = path
        self.file_list = []
        for f in os.listdir(path):
            if not 'py' in f:
                self.file_list.append(f)
        
        self.file_list = sorted(self.file_list)
        self.normalizer = normalizer
        self.train = train
        self.sampler = MAIC_Sampling(transform = transform, train = train)
        self.norm1 = Fixed_Normalizer(mean = 20.78, std = 180.50, min = -986, max = 271,  device = None)
        self.norm2 = Fixed_Normalizer(mean = 0.004, std = 0.007,  device = None)
        
    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, idx):
        current_file = os.path.join(self.path, self.file_list[idx])
        hdf_file = h5py.File(current_file , 'r')
        CT = np.array(hdf_file['CT'])
        PET = np.array(hdf_file['PET'])
        spacing = np.array(hdf_file['Size'])
        seg = np.array(hdf_file['Aorta'])
        images = np.stack((CT, PET))
        hdf_file.close()
        images, seg = self.sampler(images, seg)
        
        if self.normalizer:
            """
            images[0] = self.norm1(images[0])
            
            images[1] = (images[1] - 0.7706) / 0.6547
            """
            pet = images[1].copy()
            #images[0] = (images[0] - 1275) / 995
            #images[0][np.where(images[0] < 0)] = -200
            #images[0] = np.clip(images[0], None, 200)
            #images[1] = (images[1] - 0.14) / 0.75
            images[0] = (images[0] + 253.7455) / 417.6291
        return np.expand_dims(images[0], axis = 0), seg, spacing, np.expand_dims(images[1], axis = 0), pet