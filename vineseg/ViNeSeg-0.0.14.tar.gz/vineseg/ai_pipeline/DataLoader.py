from PIL import Image
import numpy as np
import os
from glob import glob

class Recording:
    
    def __init__( self
                , image
                , name
                ):
        self._image = image
        self._name = name 
        self._label = None
        self._has_label = False
        self._predicition = None
        self._filePath = None 
        
    @property
    def image(self):
        return self._image
    
    @image.setter
    def image(self, newImage):
        self._image = newImage

    @property
    def filePath(self):
        return self._filePath
    
    @filePath.setter
    def filePath(self, newFilePath):
        self._filePath = newFilePath
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, newName):
        self._name = newName
        
    @property
    def label(self):
        return self._label
    
    @label.setter
    def label(self, newLabel):
        self._has_label = True
        self._label = newLabel
        
    @property
    def prediction(self):
        return self._prediciton
    
    @prediction.setter
    def predicition(self, newPrediction):
        self._prediciton = newPrediction
        
    def has_label(self):
        return self._has_label
        
def data_loading( path_images, path_labels):
    recordings = []
    len_images = len(path_images)
    len_labels = len(path_labels)
    if len_labels == 0:
        path_labels = [None for _ in range(len_images)]
    for name_image, name_label in zip(path_images, path_labels):
        im_frame = Image.open(name_image)
        image = np.array(im_frame)
        name = name_image.split("/")
        name = name[-1]
        name = name.split(".")
        name = name[0]
        recording = Recording(image, name)
        recording.filePath = name_image
        if name_label != None:
            label_frame = Image.open(name_label)
            label = np.array(label_frame)
            recording.label = label
        recordings.append(recording)
    return recordings

def DataReader( list_path_images
              , list_path_mask
              , validation_frac
              ):
    number_folders = len(list_path_images)
    path_train_images = []
    path_train_segs = []
    path_val_images = []
    path_val_segs = []
    val_frac = validation_frac
    for index_folder in range(number_folders):
        images = sorted(glob(os.path.join(list_path_images[index_folder], "*")))
        if list_path_mask != []:
            segs = sorted(glob(os.path.join(list_path_mask[index_folder], "*")))
        num_total = len(images)
        for i in range(num_total):
            rann = np.random.random()
            if rann < val_frac:
                path_val_images.append(images[i])
                if list_path_mask != []:
                    path_val_segs.append(segs[i])
            else:
                path_train_images.append(images[i])
                if list_path_mask != []:
                    path_train_segs.append(segs[i])

    train_recordings = data_loading(path_train_images, path_train_segs)
    val_recordings = data_loading(path_val_images, path_val_segs)
    return train_recordings, val_recordings