import os
import datetime
import json
from types import SimpleNamespace
import h5py
import pandas as pd
import tensorflow as tf

def loadJSON(configdir):
        datapath = os.path.join(configdir,'config.json')
        print("Loading config from JSON: ", datapath)
        with open(datapath, encoding='utf-8') as infile:
            return json.loads(infile.read())
class Experiment_config(object):
    def __init__(self, params = dict()):
        if isinstance (params, str):
            tempdict = loadJSON(params)
            self.model = self.Model(tempdict.get('model'))
            self.augmentation = self.Augmentation(tempdict.get('augmentation'))
            self.data = self.Data(tempdict.get('data'))
            self.file = self.File(tempdict.get('file' ), self.model)
            # self.set_and_check_config_paths()
        else:
            self.model = self.Model(params.get('model', dict()))
            self.augmentation = self.Augmentation(params.get('augmentation', dict()))
            self.data = self.Data(params.get('data', dict()))
            self.file = self.File(params.get('file', dict()), self.model)
            # self.set_and_check_config_paths()
            if len(self.file.modelnames) < self.data.n_classes:
                self.file.modelnames = ['_'.join([self.file.experimentfolder,self.file.experimentname,"fold",str(foldnr)]) for foldnr in range(self.data.n_classes)]
                

    def toJSON(self):
        self.set_and_check_config_paths()
        print("--- saving config in model directory ---")
        print("Location: ", os.path.join(self.file.modeldir,'config.json'))
        os.makedirs(self.file.modeldir, exist_ok=True)
        with open(os.path.join(self.file.modeldir,'config.json'), 'w') as outfile:
            json.dump(self, outfile, default=lambda o: o.__dict__,sort_keys=True, indent=4)   
            
    def printParams(self):
        print("File:",json.dumps(vars(self.file),  indent=4))
        print("Data:",json.dumps(vars(self.data),  indent=4)) 
        print("Model:",json.dumps(vars(self.model),  indent=4)) 
        print("Augmentation:" ,json.dumps(vars(self.augmentation),  indent=4))
            
    def set_augmentation_params(self):
        if self.augmentation.augmentation_type == 'with_small_aug':
            self.augmentation.height_shift_range = 20
            self.augmentation.horizontal_flip = True
            self.augmentation.rotation_range = .1
            self.augmentation.shear_range = .1
            self.augmentation.vertical_flip = True
            self.augmentation.width_shift_range = .1
            self.augmentation.zoom_range = .1
        elif self.augmentation.augmentation_type == 'with_aug':
            self.augmentation.height_shift_range = 40
            self.augmentation.horizontal_flip = True
            self.augmentation.rotation_range = .2
            self.augmentation.shear_range = .2
            self.augmentation.vertical_flip = True
            self.augmentation.width_shift_range = .2
            self.augmentation.zoom_range = .2
    
    def set_and_check_config_paths(self):
        self.set_augmentation_params()
        os.makedirs(self.file.output_dir, exist_ok=True)
        os.makedirs(self.file.logdir, exist_ok=True)
        os.makedirs(self.file.modeldir, exist_ok=True)
        # self.toJSON()
    
    def check_metadata_of_dataset(self):
        print('--- checking metadata of H5 dataset ---')    
        new_dataset_needed = False
        hfile = h5py.File(self.file.h5_path, "r")
        try:
            if hfile.attrs['img_width'] != self.data.img_width: new_dataset_needed = True
            if hfile.attrs['img_height'] != self.data.img_height: new_dataset_needed = True
            if hfile.attrs['model_type'] != self.model.modeltype: new_dataset_needed = True
            if hfile.attrs['stacked'] != self.data.as_stack: new_dataset_needed = True
            if hfile.attrs['task'] != self.model.task: new_dataset_needed = True
        except:
            new_dataset_needed = True        
        hfile.close()
        return new_dataset_needed
    
    class File(object):
        def __init__(self, args, model):
            self.training_path = args.get('training_path', 'E:/MasterThesis/MA_data/ACDC/training/training/')
            self.output_dir = args.get('output_dir', os.path.abspath('../Results/Test/'))
            self.time = args.get('time', datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
            self.filename_h5 = args.get('filename_h5', "acdc_ds_"+str(model.modeltype)+".hdf5")
            self.h5_path = args.get('h5_path', os.path.join(self.output_dir, self.filename_h5))
            self.csv_name = args.get('csv_name', "acdc_ds_"+str(model.modeltype)+".csv")
            self.csv_path = args.get('csv_path', os.path.join(self.output_dir,self.csv_name))
            self.logdir = args.get('logdir', os.path.join(self.output_dir,'logs'))
            self.experimentfolder = args.get('experimentfolder', '_'.join([model.task,model.modeltype]))
            self.experimentname = args.get('experimentname', '_'.join([model.method,self.time]))
            self.modeldir = args.get('modeldir', os.path.join(os.path.join(self.output_dir, self.experimentfolder), self.experimentname))
            self.modelnames = args.get('modelnames', [])
    class Data(object):
        def __init__(self, args):  
            self.img_height = args.get('img_height',224)
            self.img_width = args.get('img_width',224)
            self.as_stack = args.get('as_stack',True)
            self.nsplits = args.get('nsplits', 5)
            self.randomstate = args.get('randomstate', 1337)
            self.withmask = args.get('withmask',False)
            self.diagnosis_dict = args.get('diagnosis_dict', {'NOR': 0, 'MINF': 1, 'DCM': 2, 'HCM': 3, 'RV': 4} )
            self.n_classes = args.get('n_classes', 5)
            if self.as_stack == True:
                self.img_shape = args.get('img_shape', (self.img_height, self.img_width,3) ) 
            else:
                 self.img_shape = args.get('img_shape', (self.img_height, self.img_width,1) ) 
    class Model(object):
        def __init__(self, args):
            self.modeltype = args.get('modeltype','vgg16')
            self.task = args.get('task', 'classification')
            self.weights = args.get('weights', None)
            self.batch_size = args.get('batch_size', 8)
            self.shuffle_buffer_size = args.get('shuffle_buffer_size', 2000)
            self.seed = args.get('seed', 3574)
            self.base_learning_rate = args.get('base_learning_rate', 1e-2)
            self.dense = args.get('dense', 1024)
            self.dropout = args.get('dropout', 0.2)
            self.method = args.get('method', 'training_from_scratch')
            self.experiment_assignment = args.get('experiment_assignment', 'ex03_gradCAM')
            self.loss_function = args.get('loss_function', 'categorical_crossentropy')
            self.activation_predictionlayer = args.get('activation_predictionlayer', 'softmax')
            self.activation_denselayer = args.get('activation_denselayer', 'relu')
            self.epochs = args.get('epochs', 200)
            self.callbacks = args.get('callbacks', [])
            self.compile_metrics = args.get('compile_metrics', ['accuracy','categorical_accuracy'])
            #TODO kernel_initializer (possibly not needed)
	        #TODO type of prediction layer
            #self.optimizer = args.get('optimizer', 
            # SGD performs better with VGG16 model instead of Adam optimizer
    class Augmentation(object):
        def __init__(self, args):
            self.augmentation_type = args.get('augmentation_type', None) #or 'with_aug", or "small_aug"
            self.rotation_range = args.get('rotation_range', None)
            self.width_shift_range = args.get('width_shift_range', None)
            self.height_shift_range = args.get('height_shift_range', None)
            self.shear_range = args.get('shear_range', None)
            self.zoom_range = args.get('zoom_range', None)
            self.horizontal_flip = args.get('horizontal_flip', False)
            self.vertical_flip = args.get('vertical_flip', False)