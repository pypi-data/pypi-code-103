import numpy as np
import nibabel as nib
import os
import cv2
import h5py
import gc
import glob
import pandas as pd
import tensorflow as tf
from . import CXAI_config
import matplotlib.pyplot as plt
from tqdm.notebook import tqdm
from sklearn.model_selection import StratifiedKFold, train_test_split
import tensorflow as tf
import h5py

class dataset_generator(CXAI_config.Experiment_config):
    """
    python class to create dataset from nii images
    """
    def __init__(self, _config, args = dict()):
        self.config = _config
        self.seg_classes = args.get('seg_classes', ['background', 'RV cavity', 'myocardium', 'LV cavity'])
        #? target_type params? this should always be the case --> why even let them be set? 
        self.target_type_min = args.get('target_type_min', 0) 
        self.target_type_max = args.get('target_type_max', 255)
        self.target_type = args.get('target_type', np.uint8)
        
        self.check_for_dataset()
        
    def check_for_dataset(self):        
        if not os.path.isfile(self.config.file.h5_path) or self.config.check_metadata_of_dataset():
            self.create_ds()
            self.config.toJSON()
            print("--- New dataset created ---")
            print("input_folder_path: ", self.config.file.training_path)
            print("output_folder_path: ", self.config.file.output_dir)
            print("output_filename: ", self.config.file.filename_h5)
            print("csv_path: ", self.config.file.csv_path)
            print("img_h: ", self.config.data.img_height)
            print("img_w: ", self.config.data.img_width)
            print("stack: ", self.config.data.as_stack)
            print("modeltype: ", self.config.model.modeltype)
            print("task: ", self.config.model.task)
        else:
            print("Dataset with specified config parameters already exists")
    
    def load_nii(self,path): # TODO put outside of class! 
        '''
        Loads nii data and returns the image data, affine data , and image header information
        Arguments:
            path: full path to the nii data
        Return:
            nimg.get_fdata(): image data
            nimg.affine: affine data
            nimg.header: image header information
        '''
        nimg = nib.load(path)
        return nimg.get_fdata(), nimg.affine, nimg.header
    
    def convert(self, img): #, target_type_min=0, target_type_max=255, target_type=np.uint8):
        '''
        Convert image/numpy array to target type with given target values.
        Modified from: https://stackoverflow.com/a/59193141
        Arguments:
            img: numpy array of image
            target_type_min: minimal value for new target format
            target_type_max: maximal value for new target format
            target_type: data type new target format
        Return:
            new_img: image/numpy array data in new target format
        '''
        a = (self.target_type_max - self.target_type_min) / (img.max() - img.min())
        b = self.target_type_max - a * img.max()
        new_img = (a * img + b).astype(self.target_type)
        return new_img
    
    def onehotencode_mask(self, mask):
        '''
        One hot encodes multiclass target labels using the number of classes as length.
        adapted from: https://github.com/hlamba28/UNET-TGS/blob/master/TGS%20UNET.ipynb
        '''
        # convert str names to class values on masks
        seg_class_values = [self.seg_classes.index(cls) for cls in self.seg_classes]
        # extract certain classes from mask (e.g. cars)
        masks = [(mask == v) for v in seg_class_values]        
        mask_stack = np.stack(masks, axis=-1).astype('float32')
        
        return mask_stack
    
    def preprocess_imgs(self, img, ismask):
        '''
        Preprocess images. Convert to target data format, resize to target size and call preprocess_input function of selected tf model.
        In case of mask only resize input.
        Arguments:
            img: numpy array of image
            ismask: If input is a segmentation mask. Default is False.
        Return:
            img: preprocessed image/numpy array
        '''
        if(ismask):
            img = cv2.resize(img, (self.config.data.img_width,self.config.data.img_height),interpolation = cv2.INTER_NEAREST)
            if self.config.model.task == 'segmentation': #? only encode it for segmentaiton or general bc dataset could be used for multiple tasks?
                img = self.onehotencode_mask(img)
            return img
        else:
            img = self.convert(img)
            img = cv2.resize(img, (self.config.data.img_width,self.config.data.img_height),interpolation = cv2.INTER_NEAREST)
            
            if self.config.model.task == "classification":
                if self.config.model.modeltype == "vgg16":
                    img = tf.keras.applications.vgg16.preprocess_input(img, data_format='channels_last') #data_format is channels_last
                elif self.config.model.modeltype == "densenet":
                    img = tf.keras.applications.densenet.preprocess_input(img, data_format='channels_last') #data_format is channels_last
                elif self.config.model.modeltype == "resnet_v2":
                    img = tf.keras.applications.resnet_v2.preprocess_input(img, data_format='channels_last') #data_format is channels_last
                #TODO: else throw exception! 
                #TODO: else option if own architecture is used!
            else:
                img = img / 255.0
        return img
    
    def create_ds (self):
        '''
        Function to generate a HDF5 file of nii images and patient infos from path. 
        Additionally generates the corresponding csv file.
        Set to fixed size and as fake RGB image or as greyscale 2D image.
        Gos trough whole directory and stores (for each patient):
            - (MRI) images
            - segmentation masks
            - diagnosis
            - weight
            - height
            - patient-ID
            - cardiac-phase
        Modified from: https://github.com/baumgach/acdc_segmenter/blob/master/acdc_data.py
        '''
        #generate HDF5 file
        hdf5_file = h5py.File(self.config.file.h5_path, "w")      

        diagnoses = []
        heights = []
        weights = []
        patient_ids = []
        cardiac_phases = []

        files = []
        num_ds_slices = 0

        #directory list of patient folders 
        dirList = os.listdir(self.config.file.training_path)
        
        #sort to ascending order (0-100)
        dirList.sort(key=sortKeyFunc)

        observerd_cols = ['patient_id','diagnosis','height','weight',
                                'ESFrame','ESFrame_height','ESFrame_width','ESFrame_slices',
                                'EDFrame','EDFrame_height','EDFrame_width','EDFrame_slices',
                                'startIdxES','endIdxES','startIdxED','endIdxED'] #TODO make it to a transfer parameter at function call or as a class attribute?
        # create empty dataframe
        df_acdc = pd.DataFrame((np.zeros((len(dirList),len(observerd_cols)))),columns=observerd_cols)

        #go through folder structure
        for j,folder in enumerate(dirList):
            folder_path = os.path.join(self.config.file.training_path, folder)
            
            if os.path.isdir(folder_path):
                #get information of patient
                infos = {}
                for line in open(os.path.join(folder_path, 'Info.cfg')):
                    label, value = line.split(':')
                    infos[label] = value.rstrip('\n').lstrip(' ')
                    
                patient_id = folder.lstrip('patient')

            for file in glob.glob(os.path.join(folder_path, 'patient???_frame??.nii.gz')):
                files.append(file)
                diagnoses.append(self.config.data.diagnosis_dict[infos['Group']])
                weights.append(infos['Weight'])
                heights.append(infos['Height'])

                patient_ids.append(patient_id)

                systole_frame = int(infos['ES'])
                diastole_frame = int(infos['ED'])
                
                file_base = file.split('.')[0]
                frame = int(file_base.split('frame')[-1])
                fileimgsize = nib.load(file).shape
                
                #save information to csv
                df_acdc.patient_id.loc[j] = patient_id #str(folder[-3:])
                df_acdc.diagnosis.loc[j] = self.config.data.diagnosis_dict[infos['Group']]
                df_acdc.height.loc[j] = infos['Height']
                df_acdc.weight.loc[j] = infos['Weight']

                if frame == systole_frame:
                    cardiac_phases.append(1)  # 1 == systole
                    df_acdc.ESFrame.loc[j] = int(infos['ES'])
                    df_acdc.ESFrame_slices.loc[j] = fileimgsize[2]
                    df_acdc.ESFrame_height.loc[j] = fileimgsize[0]
                    df_acdc.ESFrame_width.loc[j] = fileimgsize[1]
                elif frame == diastole_frame:
                    cardiac_phases.append(2)  # 2 == diastole
                    df_acdc.EDFrame.loc[j] = int(infos['ED'])
                    df_acdc.EDFrame_slices.loc[j] = fileimgsize[2]
                    df_acdc.EDFrame_height.loc[j] = fileimgsize[0]
                    df_acdc.EDFrame_width.loc[j] = fileimgsize[1]
                else:
                    cardiac_phases.append(0)  # 0 means other phase
                    
                num_ds_slices += fileimgsize[2]
        
        #save all patient information to HDF5
        enc_diagnose = np.eye(len(self.config.data.diagnosis_dict))[diagnoses]
        hdf5_file.create_dataset('diagnosis', data=np.asarray(enc_diagnose, dtype=np.uint8))
        hdf5_file.create_dataset('weight', data=np.asarray(weights, dtype=np.float32))
        hdf5_file.create_dataset('height', data=np.asarray(heights, dtype=np.float32))
        hdf5_file.create_dataset('patient', data=np.asarray(patient_ids, dtype=np.uint8))
        hdf5_file.create_dataset('cardiac_phase', data=np.asarray(cardiac_phases, dtype=np.uint8))
        
        hdf5_file.attrs['img_width'] = self.config.data.img_width
        hdf5_file.attrs['img_height'] = self.config.data.img_height
        hdf5_file.attrs['model_type'] = self.config.model.modeltype
        hdf5_file.attrs['stacked'] = self.config.data.as_stack #stack
        hdf5_file.attrs['task'] = self.config.model.task
        
        #generate HDF5 dataset for images and masks
        data = {}
        if self.config.data.as_stack == True:
            data['images'] = hdf5_file.create_dataset("images" , [num_ds_slices] + list((self.config.data.img_height, self.config.data.img_width,3)), dtype=np.float32) #unint8? otherwise othe normalization method?
        else:
            data['images'] = hdf5_file.create_dataset("images" , [num_ds_slices] + list((self.config.data.img_height, self.config.data.img_width, 1)), dtype=np.float32)
        
        if self.config.model.task == 'segmentation':
            data['masks'] = hdf5_file.create_dataset("masks" , [num_ds_slices] + list((self.config.data.img_height, self.config.data.img_width, len(self.seg_classes))), dtype=np.float32)
        else:
            data['masks'] = hdf5_file.create_dataset("masks" , [num_ds_slices] + list((self.config.data.img_height, self.config.data.img_width)), dtype=np.float32)    

        masks = []
        imgs = []
        write_buffer = 0
        counter_from = 0

        for n,file in tqdm(enumerate(files), total = len(files), desc= "Loading and preprocessing patients MRIs"):           
            file_base = file.split('.nii.gz')[0]
            file_mask = file_base + '_gt.nii.gz'

            img_dat = self.load_nii(file)
            mask_dat = self.load_nii(file_mask)
            img = img_dat[0].copy()
            mask = mask_dat[0].copy()
            
            #call resize function for all slices
            for i in range(img.shape[2]):
                img_ = img[:,:,i]
                mask_ = mask[:,:,i]
                                
                #extend to 3 channel image
                img_ = np.stack((img_,)*3, axis=-1) #TODO add if 
                
                img_r = self.preprocess_imgs(img_,ismask=False)
                mask_r = self.preprocess_imgs(mask_,ismask=True)
                                
                if self.config.data.as_stack == True:
                    imgs.append(img_r)
                else:
                    imgs.append(img_r[:,:,0].reshape((self.config.data.img_height, self.config.data.img_width,1))) #TODO check if okay for other mix of settings as well not only for "own" CNN
                                        
                masks.append(mask_r)
                                
                write_buffer += 1

                if write_buffer >= 10:
                    counter_to = counter_from + write_buffer
                    datarange_to_hdf5(data, imgs, masks, counter_from, counter_to)
                    gc_tmp(imgs, masks)

                    counter_from = counter_to
                    write_buffer = 0
        
        #write the remaing data to HDF5 file
        counter_to = counter_from + write_buffer
        datarange_to_hdf5(data, imgs, masks, counter_from, counter_to)
        gc_tmp(imgs, masks)
        
        hdf5_file.close()
        
        lastpos = 0
        for i in range(len(df_acdc)):
            df_acdc['startIdxED'].loc[i] = lastpos
            df_acdc['endIdxED'].loc[i] = lastpos+ df_acdc.loc[i].EDFrame_slices - 1
            df_acdc['startIdxES'].loc[i] = lastpos+ df_acdc.loc[i].EDFrame_slices
            df_acdc['endIdxES'].loc[i] = lastpos+ df_acdc.loc[i].EDFrame_slices + df_acdc.loc[i].ESFrame_slices - 1

            lastpos = df_acdc['endIdxES'].loc[i] + 1

        df_acdc.to_csv(self.config.file.csv_path)
        self.config.toJSON()
    
def datarange_to_hdf5(hdf5_data, img_list, mask_list, counter_from, counter_to):
    '''
    Helper function to write a range of data to the hdf5 datasets
    '''
    img_arr = np.asarray(img_list, dtype=np.float32)
    mask_arr = np.asarray(mask_list, dtype=np.float32)#dtype=np.uint8)

    hdf5_data['images'][counter_from:counter_to, ...] = img_arr
    hdf5_data['masks'][counter_from:counter_to, ...] = mask_arr

def gc_tmp(imgs, masks):
    '''
    Helper function to clear space in memory and perform garbage collection
    '''
    imgs.clear()
    masks.clear()
    gc.collect()
        
def sortKeyFunc(s, start_char_pos = 7):
    '''
    Helper function to sort folder names in ascending order (In this case after the 7 from patient_001 to patient_100).
    Starts at start_char_pos to only take the numbers into account
    '''
    return int(os.path.basename(s)[start_char_pos:])

def save_dict_to_h5(h5file, dictdata, name):
    grp = h5file.create_group(name)
    for name,data in dictdata.items():
        grp.create_dataset(name,data=data)
    return h5file

def save_splits_to_hdf5(X_train, X_valid, X_test, modeldir, experimentname):
    print("--- Saving data splits to: ", modeldir, " ---")
    with h5py.File(os.path.join(modeldir,"selected_patients.hdf5"), "w") as idx_hdf5_file:
            idx_hdf5_file.attrs['experiment'] = experimentname
            idx_hdf5_file = save_dict_to_h5(idx_hdf5_file, X_train, 'X_train')
            idx_hdf5_file = save_dict_to_h5(idx_hdf5_file, X_valid, 'X_valid')
            idx_hdf5_file = save_dict_to_h5(idx_hdf5_file, X_test, 'X_test')
    

def get_CSV(csvpath):
    return pd.read_csv(csvpath, sep=',', index_col=0)

class cv_dataloader(CXAI_config.Experiment_config):
    def __init__(self, _config, params = dict()):
        self.config = _config
        self.df = get_CSV(params.get('csv_path',self.config.file.csv_path))
        
        if not params.get('existing_selected_patients_path',False):
            print("Generating new data splits")
            self.X_train, self.X_valid, self.X_test = self.generate_cv_lists()
            save_splits_to_hdf5(self.X_train, self.X_valid, self.X_test, modeldir = self.config.file.modeldir, experimentname = self.config.file.experimentname)
            self.config.toJSON()
        else:
            print("Loading existing data splits from path ", params['existing_selected_patients_path'])
            self.X_train, self.X_valid, self.X_test = self.load_cv_lists(params['existing_selected_patients_path'])
            self.config.toJSON()
        
    def load_cv_lists(self, selected_patients_path):
        with h5py.File(selected_patients_path, "r") as f:
            return f.get('X_train'), f.get('X_valid'), f.get('X_test')

    def generate_idx_list(self,X,for_diagnosis=False):
        '''
        generates list of indices corresponding from selected patient (all slices, from start Index to end Index in csv) to the position in the HDF5 file
        Arguments:
            X: list of selected patient
            for_diagnosis: if the indices are for images or for the saved diagnoses. default is False
        Return:
            temp_idxlist: list of all indices to get the HDF5 data
        '''
        idxlist = []
        for pidx in X:
            temp = self.df[self.df.patient_id == pidx+1]
            temp_idxlist = []
            for l in range(int(temp.startIdxED.loc[temp.index.values.astype(int)[0]]),int(temp.endIdxES.loc[temp.index.values.astype(int)[0]])+1):
                if for_diagnosis:
                    temp_idxlist.append(pidx)
                else:
                    temp_idxlist.append(l)
            idxlist.append(temp_idxlist)
        return idxlist

    def get_diagnoses(self, diagnosisData, diagnosisIdxList):
        '''
        Get the corresponding diagnoses from the data (HDF5) corresponding to the selected indices.
        Arguments:
            diagnosisData: saved diagnosis data
            diagnosisIdxList: list of selected patient in dataset
        Return:
            ds_diagnoses: diagnoses data of all selected patients
        '''
        #take every second value due to double save in HDF5 (for each cardiac phase)
        temppat = diagnosisData[::2]
        ds_diagnoses = []
        
        for didx in diagnosisIdxList:
            ds_diagnoses.append(temppat[didx])
        return ds_diagnoses

    def read_h5data(self):
        '''
        Read images and diagnoses (also masks if withmask is True) from hdf5 file.
        Arguments:
            h5path: path to the hdf5 file
            withmask: if masks should also be read in and returned. Default is False
        Return:
            img: list of all images from the hdf5 file
            dia: list of all diagnoses from the hdf5 file
            mask: list of all saved segmentation masks. only if withmask = True
        '''
        #TODO: write mapping function for diagnosis/imgs/masks/etc.
        print("Loading data from HDF5 file")        
        with h5py.File(self.config.file.h5_path, "r") as f:
            diagnose_key = list(f.keys())[1]
            img_key = list(f.keys())[3]
            
            # Get the data
            dia = list(f[diagnose_key])
            img = list(f[img_key])
            
            if self.config.data.withmask:
                mask_key = list(f.keys())[4]
                mask = list(f[mask_key])
                return img, dia, mask
            return img, dia
        
    def generate_cv_lists(self, test_size=0.25, train_size=0.75):
        '''
        Generate Cross Validation (stratified k-fold) list for the number of selected folds/splits.
        Split by patient ID. Returns training/test/validation patient IDs for every fold.
        Arguments:
            csvpath: path to the csv file
            nsplits: number of splits for the stratified k-fold
            randomstate: number for random state
        Return:
            X_train: list of all training indicies (selected patients) for each fold
            X_valid: list of all validation indicies (selected patients) for each fold
            X_test: list of all test indicies (selected patients) for each fold
        '''
        pat = self.df.index.values
        diagnosis = self.df.diagnosis
        
        X_train_valid, X_test, y_train_valid, y_test, X_train, X_valid, y_train, y_valid = {},{},{},{},{},{},{},{}
        i = 0

        skf2 = StratifiedKFold(n_splits=self.config.data.nsplits, shuffle=True, random_state=self.config.data.randomstate)

        for train_valid_index, test_index in skf2.split(pat, diagnosis):
            print("Train valid index length: ",len(train_valid_index))
            print("Test index length: ",len(test_index))
            X_train_valid, X_test['fold_%s' % i] = pat[train_valid_index], pat[test_index]
            y_train_valid, y_test['fold_%s' % i] = diagnosis[train_valid_index], diagnosis[test_index]
            X_train['fold_%s' % i], X_valid['fold_%s' % i], y_train['fold_%s' % i], y_valid['fold_%s' % i] = train_test_split(X_train_valid, y_train_valid, test_size=test_size, train_size=train_size, stratify=y_train_valid, random_state=self.config.data.randomstate)
            
            print("length: X_train", len(X_train['fold_%s' % i]))
            print("length: X_valid", len(X_valid['fold_%s' % i]))
            print("length: X_test", len(X_test['fold_%s' % i]))
            
            i = i + 1
            
        return X_train, X_valid, X_test


    def generate_ds_form_cv_list(self, numOfPass):
        '''
        Generats the dataset for training/validation/test. Reads in the data for selected patients for each dataset.
        Returns all training/test/validation images and labels.
        Arguments:
            numOfPass: current number of split to select correct fold
        Return:
            train_img: list of all training images
            train_mask: list of all training masks. Only if withmask = True
            train_label: list of all training labels (diagnoses)
            test_img: list of all test images
            test_mask: list of all test masks. Only if withmask = True
            test_label: list of all test labels (diagnoses)
            val_img: list of all validation images
            val_mask: list of all validation masks. Only if withmask = True
            val_label: list of all validation labels (diagnoses)
            indices_dict: list of indices for training/test/validation for images/masks and diagnosis. For the HDF5 file
        '''
        train_img, train_label, test_img, test_label, val_img, val_label = {},{},{},{},{},{}

        train_img_idx = self.generate_idx_list(self.X_train['fold_%s' % numOfPass])
        test_img_idx = self.generate_idx_list(self.X_test['fold_%s' % numOfPass]) 
        val_img_idx = self.generate_idx_list(self.X_valid['fold_%s' % numOfPass]) 
        
        train_label_idx = self.generate_idx_list(self.X_train['fold_%s' % numOfPass], for_diagnosis=True)
        test_label_idx = self.generate_idx_list(self.X_test['fold_%s' % numOfPass],for_diagnosis=True)
        val_label_idx = self.generate_idx_list(self.X_valid['fold_%s' % numOfPass],for_diagnosis=True)
        
        indices_dict = dict({'train_img_idx':train_img_idx, 'test_img_idx':test_img_idx,'val_img_idx':val_img_idx, 
                            'train_label_idx':train_label_idx,'test_label_idx':test_label_idx, 'val_label_idx':val_label_idx,})
        
        train_img_idx = [item for sublist in train_img_idx for item in sublist]
        test_img_idx = [item for sublist in test_img_idx for item in sublist]
        val_img_idx = [item for sublist in val_img_idx for item in sublist]
        
        train_label_idx = [item for sublist in train_label_idx for item in sublist]
        test_label_idx = [item for sublist in test_label_idx for item in sublist]
        val_label_idx = [item for sublist in val_label_idx for item in sublist]

        if self.config.data.withmask: 
            img, _, mask = self.read_h5data()
            
            train_mask = [mask[x] for x in train_img_idx]
            test_mask = [mask[x] for x in test_img_idx]
            val_mask = [mask[x] for x in val_img_idx]
            
            train_img = [img[x] for x in train_img_idx]
            test_img = [img[x] for x in test_img_idx]
            val_img = [img[x] for x in val_img_idx]

            return  np.asarray(train_img), np.asarray(train_mask), np.asarray(test_img), np.asarray(test_mask), np.asarray(val_img), np.asarray(val_mask), indices_dict
            
        else:
            img, dia = self.read_h5data()
            
            train_img = [img[x] for x in train_img_idx]
            test_img = [img[x] for x in test_img_idx]
            val_img = [img[x] for x in val_img_idx]

            train_label = self.get_diagnoses(dia, train_label_idx)
            test_label = self.get_diagnoses(dia, test_label_idx)
            val_label = self.get_diagnoses(dia, val_label_idx)
            
            return np.asarray(train_img), np.asarray(train_label), np.asarray(test_img), np.asarray(test_label), np.asarray(val_img), np.asarray(val_label), indices_dict

    def get_stratified_lists(self, i=5, test_size = .15, val_size = .15, train_size = .85):
        '''
        Splits data into training, validation and test sets in a stratified way (no cross validaiton/StratifiedKFold).
        Split by patient ID. Returns all training/test/validation patient IDs for selected fold.
        Arguments:
            i: path to the hdf5 file
        Return:
            X_train: list of all training indicies (selected patients) for selected fold
            X_valid: list of all validation indicies (selected patients) for selected fold
            X_test: list of all test indicies (selected patients) for selected fold
        '''
        
        pat = self.df.index.values
        diagnosis = self.df.diagnosis 
        X_train_valid, X_test, y_train_valid, y_test, X_train, X_valid, y_train, y_valid = {},{},{},{},{},{},{},{}
        
        X_train_valid, X_test['fold_%s' % i], y_train_valid, y_test['fold_%s' % i] = train_test_split(pat, diagnosis,
                                                        stratify=diagnosis,
                                                        test_size=test_size, random_state= self.config.data.randomstate)
        
        X_train['fold_%s' % i], X_valid['fold_%s' % i], y_train['fold_%s' % i], y_valid['fold_%s' % i] = train_test_split(
            X_train_valid, y_train_valid, val_size=val_size, train_size=train_size, stratify=y_train_valid, random_state=self.config.data.randomstate)

        return X_train, X_valid, X_test
    