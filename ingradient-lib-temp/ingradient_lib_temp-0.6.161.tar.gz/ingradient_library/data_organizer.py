from ingradient_library.preprocessing import Cropping
import SimpleITK as sitk
import pickle
import os
import numpy as np
from ingradient_library.preprocessing import Resampling
import torch

class Data_Organizer(object):
    # Resampling 후 저장 추가해야 됨.
    def __init__(self, SAVE_PATH, ID = 'ingradient', resampling = None, normalizer = None, mode = 'train', do_set_direction = False):
        self.crop = Cropping()
        self.SAVE_PATH = SAVE_PATH
        self.ID = ID
        self.resampling = resampling
        self.normalizer = normalizer
        self.mode = mode
        self.do_set_direction = do_set_direction
    
    def set_direction(self, img, direction):
        direction = np.array(direction).reshape(3,3)
        inverse = np.where(direction == -1)[0]
        permute = np.where(direction != 0)[1]
        if 0 in inverse:
            img = img[::-1, :, :]

        if 1 in inverse:
            img = img[:, ::-1, :]

        if 2 in inverse:
            img = img[:, :, ::-1]

    def run(self, seg_path, img_path_list, index, modality = ['CT']):
        seg = sitk.ReadImage(seg_path)
        save_dict = dict()
        save_dict['spacing'] = seg.GetSpacing()
        save_dict['direction'] = seg.GetDirection()
        save_dict['origin'] = seg.GetOrigin()
        save_dict['modality'] = modality
        if 'CT' in modality:
            self.crop.is_CT = True
        else:
            self.crop.is_CT = False
        seg = sitk.GetArrayFromImage(seg)
        save_path = os.path.join(self.SAVE_PATH, self.ID+str(index)+'_info.pkl')
        pickle_file = open(save_path, 'wb')
        pickle.dump(save_dict, pickle_file)
        pickle_file.close()

        for i in range(len(img_path_list)):
            img_path = img_path_list[i]
            img = sitk.ReadImage(img_path)
            img = sitk.GetArrayFromImage(img)
            if len(img.shape) != 4:
                img = np.expand_dims(img, axis = 0)
            if i == 0:
                images = img
            else:
                images = np.vstack(images, img)
        
        
        print("BEFORE Cropping, current path : ", seg_path, "image shapes :", images.shape, "seg shapes :", seg.shape, "spacing :", save_dict['spacing'])
        img_arr, seg_arr = self.crop(images, seg)

        if self.do_set_direction:
            for i in range(len(images)):
                images[i] = self.set_direction(images[i], save_dict['direction'])
            
                if self.mode == 'train' :
                    seg = self.set_direction(seg, save_dict['direction'])
        
        if self.normalizer != None:
            img_arr = self.normalizer(img_arr)

        

        if self.resampling != None:
            if isinstance(img_arr, np.ndarray):
                img_arr = torch.tensor(img_arr.copy())
            else:
                img_arr = img_arr
            
            if isinstance(seg_arr, np.ndarray):
                seg_arr = torch.tensor(seg_arr.copy())
            
            else:
                seg_arr = seg_arr

            if self.mode == 'train' :
                result = self.resampling(torch.vstack((img_arr, seg_arr.unsqueeze(0))), save_dict)
                img_arr = result[:-1]
                seg_arr = result[-1].squeeze(0)
            
            else:
                img_arr = self.resampling(img_arr, save_dict)
        

        print("current path : ", seg_path, "image shapes :", img_arr.shape, "seg shapes :", seg_arr.shape, "spacing :", save_dict['spacing'])
        if isinstance(img_arr, np.ndarray):
            np.savez(os.path.join(self.SAVE_PATH, self.ID+str(index)+'.npz'), x =img_arr, y=seg_arr)
        
        else:
            np.savez(os.path.join(self.SAVE_PATH, self.ID+str(index)+'.npz'), x =img_arr.numpy(), y=seg_arr.numpy())

    