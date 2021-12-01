from numpy.random.mtrand import normal, sample
import torch
import torch.nn as nn
import torch.nn.functional as F
import SimpleITK as sitk
from torch.utils.data import Dataset
import numpy as np
import pickle
import numpy as numpy
import os
from ingradient_library.patch_transform import Batch_Affine_3D
from ingradient_library.preprocessing import *
from ingradient_library.transform import *
from torchvision.transforms import CenterCrop
import h5py


def random_axis_sample(images, seg, axis, mode = 'over'):
    if isinstance(images, np.ndarray) or isinstance(seg, np.ndarray):
        images = torch.tensor(images)
        seg = torch.tensor(seg)
    if mode == 'over':
        candidates = torch.where(seg != 0)[axis]
        index = torch.randint(low = candidates.min(), high = candidates.max() + 1, size = (1,)).item()
    
    elif mode == 'random':
        index = torch.randint(low = 0, high = seg.shape[axis], size = (1,)).item()

    if axis == 0:
        images = images[:,index]
        seg = seg[index]
    
    elif axis == 1:
        images = images[:, :, index]
        seg = seg[:, index]
    
    elif axis == 2:
        images = images[:, :, :, index]
        seg = seg[:, :, index]

    return images, seg

def set_direction(img, direction):
    if isinstance(img, np.ndarray):
        img = torch.tensor(img)
    img = img.permute(2,1,0)
    img = img.numpy()
    direction = np.array(direction).reshape(3,3)
    inverse = np.where(direction == -1)[0]
    permute = np.where(direction != 0)[1]
    img = img.transpose(permute)
    if 0 in inverse:
        img = img[::-1, :, :]

    if 1 in inverse:
        img = img[:, ::-1, :]

    if 2 in inverse:
        img = img[:, :, ::-1]

    return torch.tensor(img.copy())


class Dataset2D(Dataset):
    def __init__(self, root_dir, axis, mode, hdf_img_keys = None, train = True, hdf_seg_key = None ,sampler = None, size = (512, 512), gru_size = (512,512,512),no_sampling = False,
                oversampling = True, device = None, normalizer = None, transform = None, resample = None, correct_direction = True):

        self.file_name = []
        self.info_name = []
        for file_name in os.listdir(root_dir):
            if mode == 'npz':
                if 'npz' in file_name and not 'py' in file_name:
                    self.file_name.append(file_name)
            
                elif 'pkl' in file_name and not 'py' in file_name:
                    self.info_name.append(file_name)
            elif mode == 'hdf':
                if not 'py' in file_name and 'hdf' in file_name:
                    self.file_name.append(file_name)
        
        self.root_dir = root_dir
        self.axis = axis
        self.mode = mode
        self.hdf_img_keys = hdf_img_keys
        self.hdf_seg_key = hdf_seg_key
        self.sampler = sampler
        self.oversampling = oversampling
        self.device = device
        self.normalizer = normalizer
        self.transform = transform
        self.resample = resample
        self.correct_direction = correct_direction
        self.train = train
        self.crop = CenterCrop(size = size)
        self.no_sampling = no_sampling
        
    def __len__(self):
        return len(self.file_name)
    
    def resample(self, x, info_data, y = None):
        if self.train:
                if isinstance(y, np.ndarray):
                    y = torch.tensor(y.copy())
                result = self.resample(torch.vstack((x, y.unsqueeze(0))), info_data)
                x = result[:-1]
                y = result[-1].squeeze(0)
                return x, y
            
        else:
            x = self.resample(x, info_data)
            return x, y
    
    def __getitem__(self, idx):
        current_file = os.path.join(self.root_dir, self.file_name[idx])
        
        if self.mode == 'npz':
            info_file = open(os.path.join(self.root_dir,self.info_name[idx]), 'rb')
            info_data = pickle.load(info_file)
            info_file.close()
            data = np.load(os.path.join(self.root_dir, self.file_name[idx]))
            x = data['x']
            y = data['y']

        elif self.mode == 'hdf':
            hdf_file = h5py.File(current_file , 'r')
            first_check = True
            for h_key in self.hdf_img_keys:
                if first_check:
                    x = np.array(hdf_file[h_key])
                    first_check = False
                else:
                    x = np.stack((np.expand_dims(x, axis = 0), np.expand_dims(hdf_file[h_key], axis = 0)))
            y = np.array(hdf_file[self.hdf_seg_key[0]])
        

        if self.correct_direction:
            for i in range(len(x)):
                if i == 0:
                    result = set_direction(x[i], info_data['direction']).unsqueeze(0)
                else:
                    result = torch.vstack((result, set_direction(x[i], info_data['direction']).unsqueeze(0)))
            x = result 
            if self.train:
                y = set_direction(y, info_data['direction'])

        if self.normalizer != None:
            x = self.normalizer(x)
        
        if self.resample != None:
            x, y = self.resample(x, info_data, y)
        
        if self.sampler != None:
            x, y = self.sampler(x, y)
        
        


        if self.oversampling == False:
            return x, y
        if self.oversampling:
            temp = np.random.uniform(0, 1)
            if temp < 0.5:
                x, y = random_axis_sample(x, y, self.axis, mode = 'over')
            else:
                x, y = random_axis_sample(x, y, self.axis, mode = 'random')
        
        else:
            x, y = random_axis_sample(x, y, self.axis, mode = 'random')
    
        x = self.crop(x)
        y = self.crop(y)
        return x, y

        

class CustomDataset(Dataset):
    def __init__(self, root_dir, device = None, normalizer = None, mode = 'train', dim = '3d', correct_direction = True, resample = None):
        self.root_dir = root_dir
        self.image_name = []
        self.info_name = []
        self.device = device
        self.normalizer = normalizer
        self.mode = mode
        self.dim = dim
        self.resample = resample
        self.correct_direction = correct_direction
        if resample != None :
            self.resample.device = device
        if normalizer != None:
            self.normalizer.device = device


        for file_name in os.listdir(root_dir):            
            if 'npz' in file_name:
                self.image_name.append(file_name)
            
            elif 'pkl' in file_name:
                self.info_name.append(file_name)
                    
        self.image_name = sorted(self.image_name)
        self.info_name = sorted(self.info_name)

    def __len__(self):
        return len(self.image_name)
            
    def __getitem__(self, idx):
        info_file = open(os.path.join(self.root_dir,self.info_name[idx]), 'rb')
        info_data = pickle.load(info_file)
        info_file.close()
        data = np.load(os.path.join(self.root_dir, self.image_name[idx]))
        

        x = data['x']
        
        try: 
            y = data['y']
        except KeyError:
            print("y is missing")
            y = None
    
        if len(x.shape) == 3 and self.dim == '3d':
            #modality가 1개인 경우
            x = np.expand_dims(x, axis = 0)
        elif len(x.shape) == 2 and self.dim == '2d':
            x = np.expand_dims(x, axis = 0)

        if self.correct_direction:
            for i in range(len(x)):
                if i == 0:
                    result = set_direction(x[i], info_data['direction']).unsqueeze(0)
                else:
                    result = torch.vstack((result, set_direction(x[i], info_data['direction']).unsqueeze(0)))
            x = result 
            if self.mode == 'train' :
                y = set_direction(y, info_data['direction'])

        if self.normalizer:
            x = self.normalizer(x)
        
        
        if self.resample != None:
            if self.mode == 'train' :
                if isinstance(y, np.ndarray):
                    y = torch.tensor(y.copy())
                result = self.resample(torch.vstack((x, y.unsqueeze(0))), info_data)
                x = result[:-1]
                y = result[-1].squeeze(0)
            
            else:
                x = self.resample(x, info_data)
                
        if isinstance(x, np.ndarray):
            x = torch.tensor(x)
            

        if self.mode == 'train' :
            return x, y, info_data
        
        elif self.mode == 'test':
            return x, info_data
    
    def save_files(self, save_path, id):
        for i in range(self.__len__()):
            if self.mode == 'train':
                x, y, info_data = self.__getitem__(i)
                img_save_path = os.path.join(save_path, str(id) + '_train' + str(i) + '.npz')
                np.savez(img_save_path, x = x, y= y )
                info_save_path = os.path.join(save_path, str(id) + '_train' + str(i) + '_info.pkl')
                pickle_file = open(info_save_path, 'wb')
                pickle.dump(info_data, pickle_file)
                pickle_file.close()
            else:
                x, info_data = self.__getitem__(i)
                img_save_path = os.path.join(save_path, str(id) + '_test' + str(i) + '.npz')
                np.savez(img_save_path, x = x)
                info_save_path = os.path.join(save_path, str(id) + '_test' + str(i) + '_info.pkl')
                pickle_file = open(info_save_path, 'wb')
                pickle.dump(info_data, pickle_file)
                pickle_file.close()
            

class Dataset2point5(CustomDataset):
    def __init__(self, root_dir, degree, device=None, normalizer=None, mode='train', dim='3d', correct_direction=True, resample=None):
        super().__init__(root_dir, device=device, normalizer=normalizer, mode=mode, dim=dim, correct_direction=correct_direction, resample=resample)
        self.transform = Batch_Affine_3D([degree], [0], is_random = False)
    
    def set_direction(self, img, direction):
        return super().set_direction(img, direction)
    
    def __len__(self):
        return super().__len__()

    def __getitem__(self, idx):
        images, seg, info_data = super().__getitem__(idx) # images => n_modalities, x, y, z, seg도 마찬가지
        
        if self.transform != None:
            if isinstance(images, np.ndarray):
                images = np.expand_dims(images, aixs = 0)
            else:
                images = images.unsqueeze(0)

            if isinstance(seg, np.ndarray):
                seg = np.expand_dims(seg, axis = 0)
            else:
                seg = seg.unsqueeze(0)

            images = self.transform(images)
            seg = self.transform(seg)
            while len(images.shape) > 4:
                images = images.squeeze(0)
            while len(seg.shape) > 3:
                seg = seg.squeeze(0)


        return images, seg
    



class DataLoader3D(object):
    def __init__(self, dataset, num_iteration = 2, patch_size = (480,256,256), transform= None, device = 0, batch_size = 2, seg_one_hot = False, is_half = False, info_class = None):
        self.dataset = dataset
        self.current_index = 0
        self.patch_size = np.array(patch_size)
        self.batch_size = batch_size
        self.now_iter = 0
        self.images, self.seg, self.info = self.get_image_seg(self.current_index)
        self.device = device
        self.pass_patient_index = []
        self.num_iteration = num_iteration
        self.seg_one_hot = seg_one_hot
        self.is_half = is_half
        self.info_class = info_class #[0, 1, 3, 4] 이런식
        self.transform = transform

    
    def new_epoch(self):
        self.now_iter = 0
        self.current_index = 0
    
    def is_end(self):
        return self.current_index == len(self.dataset) and self.now_iter == 0
    
    def return_class(self):
        return np.unique(self.seg)

    def next_index(self):
        if self.now_iter == self.num_iteration:
            self.images, self.seg, self.info = self.get_image_seg(self.current_index)
            self.current_index += 1
            self.now_iter = 0
        
        else:
            self.now_iter += 1

    def get_image_seg(self, current_index): #patch size보다 전체 이미지 크기가 작을 경우 padding을 진행
        images, seg, info = self.dataset[current_index]
        if isinstance(images, np.ndarray):
            images = torch.tensor(images.copy())
        if isinstance(seg, np.ndarray):
            seg = torch.tensor(seg.copy())
        image_shape = np.array(images[0].shape)[-3:]
        if np.any(image_shape < self.patch_size):
            odd_pad = (np.max((np.array([0,0,0]),(self.patch_size - image_shape)), axis = 0) % 2 != 0).astype(int)
            even_pad = np.repeat(np.clip(((self.patch_size - image_shape)/2).astype(int), 0, np.inf), 2)
            for i in range(len(odd_pad)):
                even_pad[i*2] += odd_pad[i]
            even_pad = tuple(even_pad[::-1].astype(int).copy())
            images = F.pad(images, even_pad, "constant", 0 )
            seg = F.pad(seg, even_pad, "constant", 0 )

        return images, seg, info


    def get_oversample_patch(self, non_zero_coords, shape_to_index):
        oversample_high = np.clip(np.max(non_zero_coords, axis = 1) + 1, self.patch_size/2 - 1, shape_to_index - self.patch_size/2).reshape(1,3) + 1
        oversample_low = np.clip(np.min(non_zero_coords, axis = 1), self.patch_size/2 - 1, shape_to_index - self.patch_size/2).reshape(1,3)
        oversample_high = oversample_high.astype(int)
        oversample_low = oversample_low.astype(int)
        oversample_center = np.random.randint(oversample_low, oversample_high)

        oversample_patch_upper_bound = oversample_center + (self.patch_size/2) + 1
        oversample_patch_lower_bound = oversample_center - (self.patch_size/2 - 1)
        oversample_patch_bound = np.concatenate((oversample_patch_lower_bound.reshape(-1,1),oversample_patch_upper_bound.reshape(-1,1)), axis = 1).astype(int)
        oversample_patch_images = self.images[:, oversample_patch_bound[0][0] : oversample_patch_bound[0][1],
                                          oversample_patch_bound[1][0] : oversample_patch_bound[1][1],
                                          oversample_patch_bound[2][0] : oversample_patch_bound[2][1]]
        oversample_patch_seg = self.seg[oversample_patch_bound[0][0] : oversample_patch_bound[0][1],
                                          oversample_patch_bound[1][0] : oversample_patch_bound[1][1],
                                          oversample_patch_bound[2][0] : oversample_patch_bound[2][1]]
        
        return np.expand_dims(oversample_patch_images , axis = 0), np.expand_dims(oversample_patch_seg , axis = 0)

    def get_normal_patch(self, non_zero_coords, shape_to_index):
        normal_center = np.random.randint(low = self.patch_size/2 - 1, high = shape_to_index - (self.patch_size/2) + 1 )
        normal_patch_upper_bound = normal_center + (self.patch_size/2) + 1
        normal_patch_lower_bound = normal_center - (self.patch_size/2 - 1)
        normal_patch_bound = np.concatenate((normal_patch_lower_bound.reshape(-1,1),normal_patch_upper_bound.reshape(-1,1)), axis = 1).astype(int)
        normal_patch_images = self.images[:, normal_patch_bound[0][0] : normal_patch_bound[0][1],
                                          normal_patch_bound[1][0] : normal_patch_bound[1][1],
                                          normal_patch_bound[2][0] : normal_patch_bound[2][1]]
        normal_patch_seg = self.seg[normal_patch_bound[0][0] : normal_patch_bound[0][1],
                                          normal_patch_bound[1][0] : normal_patch_bound[1][1],
                                          normal_patch_bound[2][0] : normal_patch_bound[2][1]]
        
        return np.expand_dims(normal_patch_images , axis = 0), np.expand_dims(normal_patch_seg , axis = 0)
    



    def generate_train_batch(self):
        non_zero_coords = np.array(np.where(self.seg != 0))
        shape_to_index = np.array(self.images[0].shape) - 1 

        if self.batch_size == 1 :
            result_images, result_seg = self.get_normal_patch(non_zero_coords, shape_to_index)


        for i_b in range(self.batch_size//2): # oversample batch를 2/3 으로 바꿔야함.
            oversample_images, oversample_seg = self.get_oversample_patch(non_zero_coords, shape_to_index)
            normal_images, normal_seg = self.get_normal_patch(non_zero_coords, shape_to_index)

            if i_b == 0:
                result_images = np.concatenate((normal_images, oversample_images), axis = 0) #bs, n, x, y, z
                result_seg = np.concatenate((normal_seg, oversample_seg), axis = 0) #bs, x, y, z
            
            else:
                result_images = np.concatenate((result_images, oversample_images), axis = 0)
                result_seg = np.concatenate((result_seg, oversample_seg), axis = 0)
                result_images = np.concatenate((result_images, normal_images), axis = 0)
                result_seg = np.concatenate((result_seg, normal_seg), axis = 0)

        self.next_index()
        
    
        
        result_images = torch.Tensor(result_images).to(self.device)
        result_seg = torch.Tensor(result_seg).to(self.device)


        if self.transform:
            result_images, result_seg = self.transform(result_images, result_seg, self.info)
        
        if self.seg_one_hot:
            result_seg = F.one_hot(result_seg.long(),  num_classes = len(self.info_class)).permute(0, 4, 1, 2, 3)

        if self.is_half:
            result_images = result_images.half()
    

        return result_images, result_seg.long()


"""
class DataLoader2D(object):
    def __init__(self, dataset, batch_size = 16, full_volume_size = (600, 600, 720), transform = None):
        self.current_index = 0
        self.images, self.seg, self.info = 
        self.transform = transform
        self.current_batch = 0
        self.batch_size = batch_size
    
    def div_batch(self):
        # batch를 배수에 맞게 나눈다.
        # mat_batch를 정한다.
        
    
    def next_index(self):
        if self.current_batch == self.n_batch:
            self.images, self.seg, self.info = self.get_image_seg(self.current_index)
            self.current_index += 1
            self.now_iter = 0
        
        else:
            self.now_iter += 1

    def get_image_seg(self, current_index): #patch size보다 전체 이미지 크기가 작을 경우 padding을 진행
        images, seg, info = self.dataset[current_index]
        if isinstance(images, np.ndarray):
            images = torch.tensor(images.copy())
        if isinstance(seg, np.ndarray):
            seg = torch.tensor(seg.copy())
        image_shape = np.array(images[0].shape)[-3:]
        if np.any(image_shape < self.patch_size):
            odd_pad = (np.max((np.array([0,0,0]),(self.patch_size - image_shape)), axis = 0) % 2 != 0).astype(int)
            even_pad = np.repeat(np.clip(((self.patch_size - image_shape)/2).astype(int), 0, np.inf), 2)
            for i in range(len(odd_pad)):
                even_pad[i*2] += odd_pad[i]
            even_pad = tuple(even_pad[::-1].astype(int).copy())
            images = F.pad(images, even_pad, "constant", 0 )
            seg = F.pad(seg, even_pad, "constant", 0 )
        if len(images.shape)

        return images, seg, info
    
    def sampling_by_axis(self):
        # 축을 따라 sampling

        return
    

    def new_epoch(self):
        self.now_iter = 0
        self.current_index =

    def padding(self, image, seg):
        # 전체 Image volume을 가져올 때 padding을 진행한다.

    def get_image_seg(self, current_index):
        return super().get_image_seg(current_index) 0
    
    def next_index(self):
        if self.now_iter == self.num_iteration:
            self.images, self.seg, self.info = self.get_image_seg(self.current_index)
            self.current_index += 1
            self.now_iter = 0
        
        else:
            self.now_iter += 1

    def cal_batch(self):
        

    def generate_train_batch(self):


        
        if self.transform:
            result_images, result_seg = self.transform(result_images, result_seg, self.info)

"""



class Interactive_DataLoader(DataLoader3D):
    def __init__(self, dataset, num_iteration = 1, patch_size = (480,256,256), batch_size = 2, device = None, transform = None):
        self.dataset = dataset
        self.current_index = 0
        self.patch_size = np.array(patch_size)
        self.images, self.seg, self.info = self.get_image_seg(self.current_index)
        self.device = device
        self.num_iteration = num_iteration
        self.now_iter = 0
        self.batch_size = batch_size
        self.transform = transform
        
    def get_image_seg(self, current_index):
        return super().get_image_seg(current_index)
    
    def next_index(self):
        return super().next_index()
    
    def is_end(self):
        return super().is_end()
    
    def new_epoch(self):
        return super().new_epoch()
    
    def get_oversample_patch(self, non_zero_coords, shape_to_index):
        return super().get_oversample_patch(non_zero_coords, shape_to_index)


    """
    def generate_train_batch(self):
        oversample_images = np.expand_dims(self.images, axis = 0)
        oversample_seg = np.expand_dims(self.seg, axis = 0)
        oversample_images = torch.Tensor(oversample_images).to(self.device)
        oversample_seg = torch.Tensor(oversample_seg).to(self.device)

        if self.transform != None: 
            oversample_images, oversample_seg = self.transform(oversample_images, oversample_seg, self.info)
        oversample_seg = self.sampling(oversample_seg)

        while len(oversample_images.shape) < len(['bs', 'n_modalities', 'D', 'H', 'W']) :
            oversample_images = oversample_images.unsqueeze(0)
        self.next_index()

        return oversample_images, oversample_seg

    def sampling(self, seg):
        category = torch.unique(seg)
        random_index = torch.randint(low = 1, high = len(category), size =(1,)).to(seg.device.index)
        new_seg = (seg == category[random_index]).long()
        
        return new_seg

    """
    def generate_train_batch(self):
        non_zero_coords = np.array(np.where(self.seg != 0))
        shape_to_index = np.array(self.images[0].shape) - 1 
        oversample_images, oversample_seg = self.get_oversample_patch(non_zero_coords, shape_to_index) #bs, n, x, y,z // bs, x, y, z
        oversample_images = torch.Tensor(oversample_images).to(self.device)
        oversample_seg = torch.Tensor(oversample_seg).to(self.device)
        if self.transform != None: 
            oversample_images, oversample_seg = self.transform(oversample_images, oversample_seg, self.info)
            
        oversample_images, oversample_seg = self.sampling(oversample_images.squeeze(0), oversample_seg)
        self.next_index()

        return oversample_images, oversample_seg
        

        if self.transform != None: 
            oversample_images, oversample_seg = self.transform(oversample_images, oversample_seg, self.info)
            
        oversample_images, oversample_seg = self.sampling(oversample_images.squeeze(0), oversample_seg)
        self.next_index()

        return oversample_images, oversample_seg
        
    
    def sampling(self, images, seg):
        
        category = torch.unique(seg)
        for i in range(self.batch_size):
            random_index = torch.randint(low = 1, high = len(category), size =(1,)).to(seg.device.index)
            if i == 0:
                new_seg = (seg == category[random_index]).long()

            else:
                new_seg = torch.vstack((new_seg, (seg == category[random_index]).long()))
        new_images = torch.tile(images, [self.batch_size, *(torch.tensor(images.shape)//torch.tensor(images.shape))])

        return new_images, new_seg
    




class CustomDatasetV2(CustomDataset):
    def __init__(self, root_dir, device = None, normalizer = None, mode = 'train', dim = '3d', correct_direction = False, resample = None,
                 patch_size = (128, 128, 128), transform = None):
        
        self.patch_size = np.array(patch_size)
        self.transform = transform
        self.batch_size = 1
        super().__init__(root_dir, device = device, normalizer = normalizer, mode = mode, dim = dim, correct_direction = correct_direction, resample = resample)
    
    def __len__(self):
        return super().__len__()
    
    
    def get_oversample_patch(self, images, seg):
        if not isinstance(images, np.ndarray):
            images = images.numpy()

        if not isinstance(seg, np.ndarray):
            seg = seg.numpy()

        non_zero_coords = np.array(np.where(seg != 0))
        shape_to_index = np.array(images[0].shape) - 1 
        
        oversample_high = np.clip(np.max(non_zero_coords, axis = 1) + 1, self.patch_size/2 - 1, shape_to_index - self.patch_size/2)
        oversample_low = np.clip(np.min(non_zero_coords, axis = 1), self.patch_size/2 - 1, shape_to_index - self.patch_size/2)
        oversample_center = np.random.randint(low = oversample_low, high = oversample_high + 1)

        oversample_patch_upper_bound = oversample_center + (self.patch_size/2) + 1
        oversample_patch_lower_bound = oversample_center - (self.patch_size/2 - 1)
        oversample_patch_bound = np.concatenate((oversample_patch_lower_bound.reshape(-1,1),oversample_patch_upper_bound.reshape(-1,1)), axis = 1).astype(int)

        oversample_patch_images = images[:, oversample_patch_bound[0][0] : oversample_patch_bound[0][1],
                                          oversample_patch_bound[1][0] : oversample_patch_bound[1][1],
                                          oversample_patch_bound[2][0] : oversample_patch_bound[2][1]]
        oversample_patch_seg = seg[oversample_patch_bound[0][0] : oversample_patch_bound[0][1],
                                          oversample_patch_bound[1][0] : oversample_patch_bound[1][1],
                                          oversample_patch_bound[2][0] : oversample_patch_bound[2][1]]
        
        return np.expand_dims(oversample_patch_images , axis = 0), np.expand_dims(oversample_patch_seg , axis = 0)
    
    def get_normal_patch(self, images, seg):
        if not isinstance(images, np.ndarray):
            images = images.numpy()

        if not isinstance(seg, np.ndarray):
            seg = seg.numpy()

        shape_to_index = np.array(images[0].shape) - 1 
        normal_center = np.random.randint(low = self.patch_size/2 - 1, high = shape_to_index - (self.patch_size/2) + 1 )
        normal_patch_upper_bound = normal_center + (self.patch_size/2) + 1
        normal_patch_lower_bound = normal_center - (self.patch_size/2 - 1)
        normal_patch_bound = np.concatenate((normal_patch_lower_bound.reshape(-1,1),normal_patch_upper_bound.reshape(-1,1)), axis = 1).astype(int)
        normal_patch_images = images[:, normal_patch_bound[0][0] : normal_patch_bound[0][1],
                                          normal_patch_bound[1][0] : normal_patch_bound[1][1],
                                          normal_patch_bound[2][0] : normal_patch_bound[2][1]]
        normal_patch_seg = seg[normal_patch_bound[0][0] : normal_patch_bound[0][1],
                                          normal_patch_bound[1][0] : normal_patch_bound[1][1],
                                          normal_patch_bound[2][0] : normal_patch_bound[2][1]]
        
        return np.expand_dims(normal_patch_images , axis = 0), np.expand_dims(normal_patch_seg , axis = 0)

    
    def pad_image_seg(self, images, seg): #patch size보다 전체 이미지 크기가 작을 경우 padding을 진행
        if isinstance(images, np.ndarray):
            images = torch.tensor(images.copy())
        if isinstance(seg, np.ndarray):
            seg = torch.tensor(seg.copy())
        image_shape = np.array(images[0].shape)
        if np.any(image_shape < self.patch_size):
            odd_pad = ((self.patch_size - image_shape) % 2 != 0).astype(int)
            even_pad = np.repeat(np.clip(((self.patch_size - image_shape)/2).astype(int), 0, np.inf), 2)
            for i in range(len(odd_pad)):
                even_pad[i*2] += odd_pad[i]
            even_pad = tuple(even_pad[::-1].astype(int).copy())
            images = F.pad(images, even_pad, "constant", 0 )
            seg = F.pad(seg, even_pad, "constant", 0 )

        return images, seg

    def __getitem__(self, idx):
        info_file = open(os.path.join(self.root_dir,self.info_name[idx]), 'rb')
        info_data = pickle.load(info_file)
        info_file.close()
        data = np.load(os.path.join(self.root_dir, self.image_name[idx]))
        

        x = data['x']
        y = data['y']
        if len(x.shape) == 3 and self.dim == '3d':
            #modality가 1개인 경우
            x = np.expand_dims(x, axis = 0)
        elif len(x.shape) == 2 and self.dim == '2d':
            x = np.expand_dims(x, axis = 0)

        if self.correct_direction:
            for i in range(len(x)):
                if i == 0:
                    result = set_direction(x[i], info_data['direction']).unsqueeze(0)
                else:
                    result = torch.vstack((result, set_direction(x[i], info_data['direction']).unsqueeze(0)))
            x = result 
            if self.mode == 'train' :
                y = set_direction(y, info_data['direction'])

        if self.normalizer:
            x = self.normalizer(x)
        
        
        if self.resample != None:
            if self.mode == 'train' :
                if isinstance(y, np.ndarray):
                    y = torch.tensor(y.copy())
                result = self.resample(torch.vstack((x, y.unsqueeze(0))), info_data)
                x = result[:-1]
                y = result[-1].squeeze(0)
            
            else:
                x = self.resample(x, info_data)
        
        x, y = self.pad_image_seg(x, y)
        if self.batch_size == 1 :
            result_images, result_seg = self.get_normal_patch(x, y)


        for i_b in range(self.batch_size//2):
            oversample_images, oversample_seg = self.get_oversample_patch(x, y)
            normal_images, normal_seg = self.get_normal_patch(x, y)

            if i_b == 0:
                result_images = np.concatenate((normal_images, oversample_images), axis = 0) #bs, n, x, y, z
                result_seg = np.concatenate((normal_seg, oversample_seg), axis = 0) #bs, x, y, z
            
            else:
                result_images = np.concatenate((result_images, oversample_images), axis = 0)
                result_seg = np.concatenate((result_seg, oversample_seg), axis = 0)
                result_images = np.concatenate((result_images, normal_images), axis = 0)
                result_seg = np.concatenate((result_seg, normal_seg), axis = 0)


        if isinstance(result_images, np.ndarray):
            result_images = torch.tensor(result_images)
        
        if isinstance(result_seg, np.ndarray):
            result_seg = torch.tensor(result_seg)
        
        if result_images.device.index != self.device:
            result_images = result_images.to(self.device)

        if result_seg.device.index != self.device:
            result_seg = result_seg.to(self.device)

        if self.transform:
            result_images, result_seg = self.transform(result_images.to(self.device), result_seg.to(self.device), info_data)
        

        return result_images.squeeze(0), result_seg.squeeze(0).long(), info_data

    

"""
class DataLoader2D(object):
    def __init__(self, patch_size = , batch_size = 8, ):


    def new_epoch(self):
        self.now_iter = 0
        self.current_index = 0
    
    def is_end(self):
        return self.current_index == len(self.dataset) and self.now_iter == 0
    
    def return_class(self):
        return np.unique(self.seg)

    def next_index(self):
        if self.now_iter == self.num_iteration:
            self.images, self.seg, self.info = self.get_image_seg(self.current_index)
            self.current_index += 1
            self.now_iter = 0
        
        else:
            self.now_iter += 1

    def generate_train_batch(self):
"""

