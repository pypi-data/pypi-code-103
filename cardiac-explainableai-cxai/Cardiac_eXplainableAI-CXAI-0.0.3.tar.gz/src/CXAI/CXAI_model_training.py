# Helper libraries
import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime
import pandas as pd
import h5py
from . import CXAI_config
from . import CXAI_dataloader
from . import CXAI_evaluation
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, concatenate, Conv2D, MaxPooling2D, Conv2DTranspose, BatchNormalization, Dropout, Lambda, UpSampling2D
from tensorflow.keras import backend as K
tf.debugging.set_log_device_placement(False)
print(tf.config.experimental.list_physical_devices('GPU'))

class model_training(CXAI_dataloader.cv_dataloader):
    def __init__(self, _config, _dataloader, params = dict()):
        self.config = _config
        self.dataloader = _dataloader

    def Unet(self):
        #! work in progress
        self.inputs = Input((self.config.data.img_height, self.config.data.img_width, 3))
        #s = Lambda(lambda x: x / 255)(inputs)   #No need for this if we normalize our inputs beforehand
        # s = inputs

        #Contraction path
        c1 = Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(self.inputs)
        c1 = Dropout(0.1)(c1)
        c1 = Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c1)
        p1 = MaxPooling2D((2, 2))(c1)
        
        c2 = Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(p1)
        c2 = Dropout(0.1)(c2)
        c2 = Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c2)
        p2 = MaxPooling2D((2, 2))(c2)
        
        c3 = Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(p2)
        c3 = Dropout(0.2)(c3)
        c3 = Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c3)
        p3 = MaxPooling2D((2, 2))(c3)
        
        c4 = Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(p3)
        c4 = Dropout(0.2)(c4)
        c4 = Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c4)
        p4 = MaxPooling2D(pool_size=(2, 2))(c4)
        
        c5 = Conv2D(256, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(p4)
        c5 = Dropout(0.3)(c5)
        c5 = Conv2D(256, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c5)
        
        #Expansive path 
        u6 = Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(c5)
        u6 = concatenate([u6, c4])
        c6 = Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(u6)
        c6 = Dropout(0.2)(c6)
        c6 = Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c6)
        
        u7 = Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(c6)
        u7 = concatenate([u7, c3])
        c7 = Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(u7)
        c7 = Dropout(0.2)(c7)
        c7 = Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c7)
        
        u8 = Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same')(c7)
        u8 = concatenate([u8, c2])
        c8 = Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(u8)
        c8 = Dropout(0.1)(c8)
        c8 = Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c8)
        
        u9 = Conv2DTranspose(16, (2, 2), strides=(2, 2), padding='same')(c8)
        u9 = concatenate([u9, c1], axis=3)
        c9 = Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(u9)
        c9 = Dropout(0.1)(c9)
        c9 = Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c9)
        
        outputs = Conv2D(3, (1, 1), activation='softmax')(c9)
        model = Model(inputs=[self.inputs], outputs=[outputs])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3), loss='categorical_crossentropy', metrics=['accuracy'])#metrics=[tf.keras.metrics.MeanIoU(num_classes=2)]) #metrics=['accuracy'])
        print(model.summary())
        return model    

    def classificationCNN(self):
        print(self.config.data.img_shape)
        
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Conv2D(filters = 16, kernel_size=(7,7), padding='valid', input_shape = self.config.data.img_shape))
        model.add(tf.keras.layers.BatchNormalization())
        model.add(tf.keras.layers.Activation('relu'))

        model.add(tf.keras.layers.Conv2D(filters = 32, kernel_size=(5,5), padding='valid'))
        model.add(tf.keras.layers.BatchNormalization())
        model.add(tf.keras.layers.Activation('relu'))

        model.add(tf.keras.layers.Conv2D(filters = 32, kernel_size=(3,3), padding='valid'))
        model.add(tf.keras.layers.BatchNormalization())
        model.add(tf.keras.layers.Activation('relu'))

        model.add(tf.keras.layers.MaxPool2D(pool_size=(2, 2)))

        model.add(tf.keras.layers.Conv2D(filters = 64, kernel_size=(3,3), padding='valid'))
        model.add(tf.keras.layers.BatchNormalization())
        model.add(tf.keras.layers.Activation('relu'))

        model.add(tf.keras.layers.Conv2D(filters = 64, kernel_size=(3,3), padding='valid'))
        model.add(tf.keras.layers.BatchNormalization())
        model.add(tf.keras.layers.Activation('relu'))

        model.add(tf.keras.layers.MaxPool2D(pool_size=(2, 2)))

        model.add(tf.keras.layers.Conv2D(filters = 128, kernel_size=(3,3), padding='valid'))
        model.add(tf.keras.layers.BatchNormalization())
        model.add(tf.keras.layers.Activation('relu'))

        model.add(tf.keras.layers.Conv2D(filters = 128, kernel_size=(3,3), padding='valid'))
        model.add(tf.keras.layers.BatchNormalization())
        model.add(tf.keras.layers.Activation('relu'))

        model.add(tf.keras.layers.Conv2D(filters = 128, kernel_size=(3,3), padding='valid'))
        model.add(tf.keras.layers.BatchNormalization())
        model.add(tf.keras.layers.Activation('relu'))

        model.add(tf.keras.layers.MaxPool2D(pool_size=(2, 2)))

        model.add(tf.keras.layers.Conv2D(filters = 256, kernel_size=(3,3), padding='valid'))
        model.add(tf.keras.layers.BatchNormalization())
        model.add(tf.keras.layers.Activation('relu'))

        model.add(tf.keras.layers.Conv2D(filters = 256, kernel_size=(3,3), padding='valid'))
        model.add(tf.keras.layers.BatchNormalization())
        model.add(tf.keras.layers.Activation('relu'))

        model.add(tf.keras.layers.Conv2D(filters = 256, kernel_size=(3,3), padding='valid'))
        model.add(tf.keras.layers.BatchNormalization())
        model.add(tf.keras.layers.Activation('relu'))

        model.add(tf.keras.layers.GlobalAveragePooling2D())
        model.add(tf.keras.layers.Dense(self.config.model.dense, activation=self.config.model.activation_denselayer))
        model.add(tf.keras.layers.Dropout(self.config.model.dropout))
        model.add(tf.keras.layers.Dense(len(self.config.data.diagnosis_dict), activation=self.config.model.activation_predictionlayer, name="prediction"))
        
        opt = tf.keras.optimizers.Adam(lr=self.config.model.base_learning_rate)
        model.compile(loss=self.config.model.loss_function, optimizer=opt,metrics=self.config.model.compile_metrics)
        print(model.summary())
        
        return model
        
    def generate_model(self, optimizer):
        if self.config.model.task == "classification":
            if self.config.model.modeltype == "vgg16":
                appmodel = tf.keras.applications.VGG16(input_shape=self.config.data.img_shape, include_top=False, weights=self.config.model.weights)
                # opt = tf.keras.optimizers.SGD(lr=self.config.model.base_learning_rate)

            elif self.config.model.modeltype == "densenet":
                appmodel = tf.keras.applications.DenseNet121(input_shape=self.config.data.img_shape,include_top=False,weights=self.config.model.weights)
                # opt = tf.keras.optimizers.Adam(lr=self.config.model.base_learning_rate)

            elif self.config.model.modeltype == "resnet_v2":
                appmodel = tf.keras.applications.ResNet50V2(input_shape=self.config.data.img_shape,include_top=False,weights=self.config.model.weights)
                # opt = tf.keras.optimizers.Adam(lr=self.config.model.base_learning_rate)

            avgpool = tf.keras.layers.GlobalAveragePooling2D()(appmodel.output)
            fc1 = tf.keras.layers.Dense(self.config.model.dense, activation=self.config.model.activation_denselayer)(avgpool)
            dropout = tf.keras.layers.Dropout(self.config.model.dropout)(fc1)
            fc2 = tf.keras.layers.Dense(len(self.config.data.diagnosis_dict), activation=self.config.model.activation_predictionlayer, name="prediction")(dropout)

            model = tf.keras.models.Model(inputs=appmodel.input, outputs=fc2)
            model.compile(loss= self.config.model.loss_function,optimizer=optimizer,metrics=self.config.model.compile_metrics)
            print(model.summary())
            return model
        elif self.config.model.task == "segmentation":
            return self.Unet()
        
    def getTrainValTestBatches(self, foldnr):
        train_img,train_label,test_img,test_label,val_img,val_label,temp_idx = self.dataloader.generate_ds_form_cv_list(numOfPass=foldnr)
        
        print(np.shape(train_img))
        print(np.shape(train_label))

        if self.config.augmentation.augmentation_type:
            train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rotation_range=self.config.augmentation.rotation_range,
                                                                        width_shift_range=self.config.augmentation.width_shift_range,
                                                                        height_shift_range=self.config.augmentation.height_shift_range,
                                                                        shear_range=self.config.augmentation.shear_range,
                                                                        zoom_range=self.config.augmentation.zoom_range,
                                                                        horizontal_flip=self.config.augmentation.horizontal_flip,
                                                                        vertical_flip=self.config.augmentation.vertical_flip)
            train_batches = train_datagen.flow(train_img,train_label, batch_size=self.config.model.batch_size, shuffle=True, seed=self.config.model.seed)
            model_steps_per_epoch = train_batches.n // train_batches.batch_size
        else:
            train = tf.data.Dataset.from_tensor_slices((train_img,train_label))
            train_batches = train.shuffle(self.config.model.shuffle_buffer_size, seed=self.config.model.seed).batch(self.config.model.batch_size)
            model_steps_per_epoch = None

        val = tf.data.Dataset.from_tensor_slices((val_img,val_label))
        test = tf.data.Dataset.from_tensor_slices((test_img,test_label))

        validation_batches = val.batch(self.config.model.batch_size)
        test_batches = test.batch(self.config.model.batch_size)
        return train_batches, validation_batches, test_batches, model_steps_per_epoch, test_img, test_label
    
    def generateCallbacks(self, modelname_path, modelname):
        tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=os.path.join(self.config.file.logdir, modelname), histogram_freq=0, write_graph=True,
            write_images=True)

        checkpoint = tf.keras.callbacks.ModelCheckpoint(modelname_path,
                                                        monitor='val_loss', verbose=1,
                                                        save_best_only=True, mode='min')
        
        early_stopping =  tf.keras.callbacks.EarlyStopping(monitor="val_loss",min_delta=1e-4,
                                                        patience=10,verbose=1)

        lr_scheduler = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss',factor=0.1, patience=5,
                                                            verbose=1, cooldown=0, min_lr=1e-11)

        csv_logger = tf.keras.callbacks.CSVLogger(os.path.join(self.config.file.modeldir, str(modelname) + '_traininglog.csv'))
        
        return [early_stopping,checkpoint, tensorboard_callback, lr_scheduler, csv_logger]
        

    def train_model(self, own_model = False, callback = False, optimizer = False):    
        self.config.set_and_check_config_paths()
        self.config.toJSON()
        
        tf.keras.backend.clear_session()
        allresults, cv_acc, cv_loss, = [],[],[]
        
        for foldnr in range(self.config.data.nsplits):
            train_batches, validation_batches, test_batches, model_steps_per_epoch, test_img, test_label = self.getTrainValTestBatches(foldnr)
            
            if optimizer == False:
                optimizer = tf.keras.optimizers.SGD(lr=self.config.model.base_learning_rate) if self.config.model.modeltype == 'vgg16' else tf.keras.optimizers.Adam(lr=self.config.model.base_learning_rate) 

            if not own_model:
                model = self.generate_model(optimizer)
            else:
                model = tf.keras.models.clone_model(own_model)
                model.compile(loss=self.config.model.loss_function, optimizer=optimizer,metrics=self.config.model.compile_metrics)

            modelname_path = os.path.join(self.config.file.modeldir, str(self.config.file.modelnames[foldnr]) + ".h5")
            
            if callback == False:
                callbacks = self.generateCallbacks(modelname_path, self.config.file.modelnames[foldnr])
           
            model.fit(train_batches,
                        steps_per_epoch = model_steps_per_epoch,
                        epochs=self.config.model.epochs,
                        validation_data=validation_batches,
                        callbacks= callbacks)

            model = tf.keras.models.load_model(modelname_path)

            results = model.evaluate(test_batches)
            results = dict(zip(model.metrics_names,results))
            
            print(results)
            # print("Early stopping from epoch: ", early_stopping.stopped_epoch) #! save this info somewhere as well
            
            allresults.append(results)
            cv_acc.append(results['accuracy'])
            cv_loss.append(results['loss'])

            CXAI_evaluation.classification_evaluation_with_auc(model_config=self.config, modelpath=modelname_path, test_img=test_img, test_label=test_label)
            tf.keras.backend.clear_session()

        print("Average Test Accuracy for " + str(self.config.file.experimentname) + " with " + str(self.config.data.nsplits) + " folds",round(np.mean(cv_acc),3))

        summary_csv_path = os.path.join(self.config.file.output_dir,'_'.join([self.config.model.experiment_assignment,self.config.model.task,"overview.csv"]))
        df, maxnewidx = check_for_overall_experiment_csv(summary_csv_path)
        df.loc[maxnewidx,'model_dir_path'] = self.config.file.modeldir
        df.loc[maxnewidx,'method'] = self.config.model.method
        df.loc[maxnewidx,'modeltype'] = self.config.model.modeltype
        df.loc[maxnewidx,'num_CV'] = self.config.data.nsplits
        df.loc[maxnewidx,'avg_acc'] = round(np.mean(cv_acc),3)

        df.reset_index(drop=True,inplace=True)
        df.to_csv(summary_csv_path,sep=',')

def check_for_overall_experiment_csv(path_to_summary_csv):
    if os.path.isfile(path_to_summary_csv):
        df = pd.read_csv(path_to_summary_csv, sep=',', index_col=0)
        return df, len(df)
    else:
        return pd.DataFrame(columns=['model_dir_path','method','modeltype','num_CV','avg_acc']), 0