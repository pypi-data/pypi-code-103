import scipy.io as sci_io                                           # for loading .mat files
import pandas as pd                                                 # for dataframes
import os                                                           # get/change working directory
import random                                                       # pseudo-random numbers
from IPython.display import clear_output                            # for Jupyter 


import tensorflow as tf
from tensorflow import keras                                        # using Keras API to simplify TF workflows

from tensorflow.keras.applications.densenet import preprocess_input 
from tensorflow.keras.applications.densenet import DenseNet201


from tensorflow.keras.preprocessing.image import ImageDataGenerator # pipeline for feature extraction
from tensorflow.keras.models import Model                           # for manipulating Tensorflow models
from tensorflow.keras import layers                                 # for manipulating Tensorflow models
from tensorflow.keras import optimizers                             # for manipulating Tensorflow models
from tensorflow.keras import metrics                                # for manipulating Tensorflow models
from tensorflow.keras.applications import densenet                  # for manipulating Tensorflow models
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, CSVLogger, LearningRateScheduler
                                                                    # per epoch callbacks for saving model, early stopping, logging progress and changing learning rate
from livelossplot import PlotLossesKerasTF                          # plotting training progress

import numpy as np                                                  # using numpy for arrays
from sklearn.metrics import silhouette_score                        # silhouette coefficient to test embeddings separation
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA                               # dimensionality reduction
from joblib import dump, load                                       # PCA model persistence


import matplotlib.pyplot as plt


def load_data (PROJECT_FOLDER):
    # loading data from matlab files into pandas dataframes
    def iter_dict(input_dict,input_meta):
        num_records = input_dict['annotations'].shape[1]
        df_output = pd.DataFrame (columns = ['class', 'file_name', 'class_name', 'year', 'brand', 'model','bbox_x1','bbox_x2','bbox_y1','bbox_y2'])

        for i in range(num_records):
            class_label = int(input_dict['annotations']['class'][0][i][0][0])
            bbox_x1 = int(input_dict['annotations']['bbox_x1'][0][i][0][0])
            bbox_x2 = int(input_dict['annotations']['bbox_x2'][0][i][0][0])
            bbox_y1 = int(input_dict['annotations']['bbox_y1'][0][i][0][0])
            bbox_y2 = int(input_dict['annotations']['bbox_y2'][0][i][0][0])
            class_name = input_meta['class_names'][0][class_label-1][0]
            file_name = input_dict['annotations']['fname'][0][i][0]
            man_year = input_meta['class_names'][0][class_label-1][0].split()[-1]
            brand = input_meta['class_names'][0][class_label-1][0].split()[0]
            model = input_meta['class_names'][0][class_label-1][0].replace(man_year,"").replace(brand,"")

            data_dict = {'class': class_label, 'file_name': file_name, 'class_name':class_name, 'year':man_year, 'brand':brand, 'model':model, 'bbox_x1':bbox_x1,'bbox_x2':bbox_x2,'bbox_y1':bbox_y1,'bbox_y2':bbox_y2}
            df_output= df_output.append(data_dict,ignore_index=True)

        return df_output
    
    annot_train = sci_io.loadmat(PROJECT_FOLDER+'cars_train_annos.mat')
    annot_test = sci_io.loadmat(PROJECT_FOLDER+'cars_test_annos_withlabels.mat')
    cars_meta = sci_io.loadmat(PROJECT_FOLDER+'cars_meta.mat')
 
    return iter_dict(annot_train,cars_meta), iter_dict(annot_test,cars_meta)


def extract_features(path, emb_model, target_size = (224,224)):
    image_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
    data_generator = image_datagen.flow_from_directory(path, target_size=target_size,shuffle=False)
    features = emb_model.predict(data_generator)
    features = np.array(features)
    return features

def test_classifier (df_test, img_path, model, params):
    batch_size = params['batch_size']
    target_size = params['target_size']
    gen_df = pd.DataFrame()
    gen_df['filename'] = (img_path + df_test.file_name)
    gen_df['class'] = df_test['class'].astype(str)

    test_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
    test_generator = test_datagen.flow_from_dataframe(dataframe=gen_df,class_mode="categorical", target_size=target_size,shuffle=False, batch_size=batch_size,subset='training', seed=111)

    return model.evaluate(test_generator)


def train_classifier(df_train,PROJECT_FOLDER,img_path, model, params):
    epochs = params['epochs']
    target_size = params['target_size']
    shape = target_size + (3,)
    batch_size = params['batch_size']
    prefix = params['prefix']
    backbone = params['backbone']
    learning_rate = params['learning_rate']
    augmentation = params['augmentation']
    checkpoint_file = params['checkpoint_file']
    continue_training = params['continue_training']
    num_classes = df_train['class'].nunique()
    gen_df = pd.DataFrame()
    gen_df['filename'] = (img_path + df_train.file_name)
    gen_df['class'] = df_train['class'].astype(str)

    gen_df_train=gen_df.sample(frac=0.8,random_state=200) 
    gen_df_val=gen_df.drop(gen_df_train.index)



    #image preprocessing and augmentation
    if augmentation:
        train_datagen = ImageDataGenerator(
                    horizontal_flip=True,
                    rotation_range=0.45,
                    height_shift_range=0.2,
                    width_shift_range=0.2,
                    preprocessing_function=preprocess_input)
    else:
        train_datagen = ImageDataGenerator(
                    preprocessing_function=preprocess_input)

    val_datagen = ImageDataGenerator(                
                    preprocessing_function=preprocess_input,
                    validation_split=0.99999)


    #loading training data into batches along with the labels

    training_generator = train_datagen.flow_from_dataframe(dataframe=gen_df_train,class_mode="categorical", target_size=target_size,shuffle=False, batch_size=batch_size,subset='training', seed=111)
    validation_generator = val_datagen.flow_from_dataframe(dataframe=gen_df_val,class_mode="categorical", target_size=target_size,shuffle=False, batch_size=batch_size,subset='validation', seed=111)

    #for DenseNet201 unfreeze from "conv5_block1_0_bn", see https://arxiv.org/ftp/arxiv/papers/2110/2110.05270.pdf

    trainable = False
    for layer in model.layers:
        if layer.name == "conv5_block1_0_bn":
            trainable = True
        layer.trainable = trainable

    #adding a couple of layers to step down

    flatten = layers.Flatten() (model.output)
    dense1 = layers.Dense(units = 512, activation='relu') (flatten)
    dropout1 = layers.Dropout(0.5)(dense1)
    output = layers.Dense(units=num_classes, activation='softmax') (dropout1)

    plot_loss_1 = PlotLossesKerasTF()

    early_stop = EarlyStopping(monitor='val_loss',
                           patience=5,
                           restore_best_weights=True,
                           mode='min')


    classifier_model = Model(inputs=model.input, outputs=output, name="classifier_model")
    classifier_model.compile(loss="categorical_crossentropy",optimizer=optimizers.Adam(learning_rate),metrics=[keras.metrics.TopKCategoricalAccuracy(k=1,name = 'top1'),keras.metrics.TopKCategoricalAccuracy(k=5,name='top5')])


    save_to = PROJECT_FOLDER+"models/" +prefix + backbone +'_LR'+str(learning_rate) + '_'+'{epoch:02d}-{val_loss:.2f}.hdf5'
    csv_logger = CSVLogger(PROJECT_FOLDER+"models/" +prefix+ backbone +'_LR'+str(learning_rate) +'.log')
    
    callbacks = [
        ModelCheckpoint(save_to, save_weights_only=True,save_freq='epoch',verbose=1),
        csv_logger,
        early_stop, 
        plot_loss_1,
        keras.callbacks.ReduceLROnPlateau(patience=4, verbose=1,cooldown=4),
        ]

    if checkpoint_file != '':
        classifier_model.load_weights(checkpoint_file)

    if continue_training :
        classifier_model.fit(training_generator, epochs=epochs, validation_data=validation_generator ,callbacks=callbacks,verbose=1)


    return classifier_model


def generate_random_triplets (df_train,TRAIN_FOLDER_IMAGES):
    df_triplets = pd.DataFrame (columns=['anchor','positive','negative'])
    car_class = ''
    max_positive = ''
    max_negative = ''
    for x, row in df_train.iterrows():
        if row['class'] != car_class:
            df_positive = df_train[df_train['class']==row['class']] #selecting positives from images of the same class
            df_negative = df_train[df_train['brand']!=row['brand']] #selecting negatives from other brands
            df_positive.reset_index(drop=True,inplace = True)
            df_negative.reset_index(drop=True,inplace = True)
            max_positive = len(df_positive)
            max_negative = len(df_negative)
            car_class = row['class']

        for y in range(0,max_positive):       
            anchor_file = "../"+ TRAIN_FOLDER_IMAGES + row['file_name']
            pos_file = "../" + TRAIN_FOLDER_IMAGES + df_positive['file_name'][y]
            neg_file = "../" + TRAIN_FOLDER_IMAGES + df_negative['file_name'][random.randint(0,max_negative-1)]
            if pos_file != anchor_file:
                line_item = {'anchor':anchor_file,'positive':pos_file,'negative':neg_file}
                df_triplets = df_triplets.append(line_item,ignore_index=True)

        clear_output(wait=True)
        print('row done: ' + str(x) )
        print('triplet count: ' + str(len(df_triplets)) )
    print(df_triplets)
    df_triplets.to_csv('random_triplets.csv',index=False)
    return df_triplets


def generate_hard_triplets (df_train, TRAIN_FOLDER_IMAGES, train_features): #hard negative and hard positive triplet mining, idea based on the FaceNet paper
    df_train_features = pd.DataFrame(train_features)
    df_train_merged = pd.merge(df_train, df_train_features,left_index=True, right_index=True)
    feat_start = -1920
    feat_end = len(df_train_merged.columns)
    
    df_triplets = pd.DataFrame (columns=['anchor','positive','negative'])

    for x, row in df_train_merged.iterrows():
        
        selected_features =  np.array(df_train_merged.iloc[x,feat_start:feat_end]).reshape(1,-1)
        all_other_features = df_train_merged[df_train_merged['class']==row['class']].iloc[:,feat_start:feat_end]
        all_other_features.drop(x,axis=0,inplace=True)
        similarities = cosine_similarity(selected_features, all_other_features)
        hard_positive_ix = all_other_features.index[similarities.argmin()]

        all_other_features =df_train_merged[df_train_merged['brand']!=row['brand']].iloc[:,feat_start:feat_end]
        similarities = cosine_similarity(selected_features, all_other_features)
        hard_negative_ix = all_other_features.index[similarities.argmax()]
        
        anchor_file = "../"+ TRAIN_FOLDER_IMAGES + row['file_name']
        pos_file = "../" + TRAIN_FOLDER_IMAGES + df_train_merged['file_name'][hard_positive_ix]
        neg_file = "../" + TRAIN_FOLDER_IMAGES + df_train_merged['file_name'][hard_negative_ix]
        line_item = {'anchor':anchor_file,'positive':pos_file,'negative':neg_file}
        df_triplets = df_triplets.append(line_item,ignore_index=True)

        clear_output(wait=True)
        print('row done: ' + str(x) )
        print('triplet count: ' + str(len(df_triplets)) )
        #print(line_item)
    print(df_triplets)
    df_triplets.to_csv('hard_triplets_densenet.csv',index=False)
    return df_triplets

def visualize(anchor, positive, negative):
    """Visualize a few triplets from the supplied batches."""

    def show(ax, image):
        ax.imshow(image)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

    fig = plt.figure(figsize=(9, 9))

    axs = fig.subplots(3, 3)
    for i in range(3):
        show(axs[i, 0], anchor[i])
        show(axs[i, 1], positive[i])
        show(axs[i, 2], negative[i])


#siamese code adapted from: https://keras.io/examples/vision/siamese_network/
#https://colab.research.google.com/github/keras-team/keras-io/blob/master/examples/vision/ipynb/siamese_network.ipynb        
        
def train_siamese (PROJECT_FOLDER, triplets_file, params):
    epochs = params['epochs']
    target_shape = params['target_size']
    batch_size = params['batch_size']
    prefix = params['prefix']
    backbone = params['backbone']
    learning_rate = params['learning_rate']
    checkpoint_file = params['checkpoint_file']
    continue_training = params['continue_training']


    #functions to load and preprocess images
    #---------------------------------------


    def preprocess_image(filename):
        """
        Load the specified file as a JPEG image, preprocess it and
        resize it to the target shape.
        """
        image_string = tf.io.read_file(filename)
        image = tf.image.decode_jpeg(image_string, channels=3)
        image = tf.image.convert_image_dtype(image, tf.float32)
        image = tf.image.resize(image, target_shape,method='area') #this will lead to loss of aspect ratio, but it might not be an issue for this purpose

        return image


    def preprocess_triplets(anchor, positive, negative):
        """
        Given the filenames corresponding to the three images, load and
        preprocess them.
        """

        return (
            preprocess_image(anchor),
            preprocess_image(positive),
            preprocess_image(negative),
        )

    #data pipelines
    #--------------

    df = pd.read_csv(triplets_file, header = 0)    

    df = df.replace(r"\.\.\/",PROJECT_FOLDER,regex=True)

    anchor_images = np.array(df.anchor)
    positive_images = np.array(df.positive)
    negative_images = np.array(df.negative)

    image_count = len(anchor_images)
    print(image_count)

    anchor_dataset = tf.data.Dataset.from_tensor_slices(anchor_images)
    positive_dataset = tf.data.Dataset.from_tensor_slices(positive_images)
    negative_dataset = tf.data.Dataset.from_tensor_slices(negative_images)

    print('datasets created')

    dataset = tf.data.Dataset.zip((anchor_dataset, positive_dataset, negative_dataset))
    dataset = dataset.shuffle(buffer_size=1024)
    dataset = dataset.map(preprocess_triplets)

    print('triplets created')


    # Let's now split our dataset in train and validation.
    train_dataset = dataset.take(round(image_count * 0.8))
    val_dataset = dataset.skip(round(image_count * 0.8)) #20% validation is causing large pauses at the end of each epoch

    train_dataset = train_dataset.batch(batch_size, drop_remainder=False)
    train_dataset = train_dataset.prefetch(4)

    val_dataset = val_dataset.batch(batch_size, drop_remainder=False)
    val_dataset = val_dataset.prefetch(4)

    visualize(*list(train_dataset.take(1).as_numpy_iterator())[0])


    #base pre-trained neural network
    #-------------------------------

    #base_cnn = resnet.ResNet50(
    #    weights="imagenet", input_shape=target_shape + (3,), include_top=False
    #)

    base_cnn = DenseNet201(
        weights="imagenet", input_shape=target_shape + (3,), include_top=False
    )

    flatten = layers.Flatten()(base_cnn.output)
    dense1 = layers.Dense(512, activation="relu")(flatten)
    dense1 = layers.BatchNormalization()(dense1)
    dense2 = layers.Dense(256, activation="relu")(dense1)
    dense2 = layers.BatchNormalization()(dense2)
    output = layers.Dense(256)(dense2)

    embedding = Model(base_cnn.input, output, name="Embedding")

    # for resnet50 unfreeze from "conv5_block1_out"
    #trainable = False
    #for layer in base_cnn.layers:
    #    if layer.name == "conv5_block1_out":
    #        trainable = True
    #    layer.trainable = trainable
        
    #for DenseNet201 unfreeze from "conv5_block1_0_bn", see https://arxiv.org/ftp/arxiv/papers/2110/2110.05270.pdf
    trainable = False
    for layer in base_cnn.layers:
        if layer.name == "conv5_block1_0_bn":
            trainable = True
        layer.trainable = trainable

    #custom distance layer for the Siamese network
    #---------------------------------------------

    class DistanceLayer(layers.Layer):
        """
        This layer is responsible for computing the distance between the anchor
        embedding and the positive embedding, and the anchor embedding and the
        negative embedding.
        """

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def call(self, anchor, positive, negative):
            ap_distance = tf.reduce_sum(tf.square(anchor - positive), -1)
            an_distance = tf.reduce_sum(tf.square(anchor - negative), -1)
            return (ap_distance, an_distance)


    anchor_input = layers.Input(name="anchor", shape=target_shape + (3,))
    positive_input = layers.Input(name="positive", shape=target_shape + (3,))
    negative_input = layers.Input(name="negative", shape=target_shape + (3,))

    distances = DistanceLayer()(
        embedding(preprocess_input(anchor_input)),
        embedding(preprocess_input(positive_input)),
        embedding(preprocess_input(negative_input)),
    )

    siamese_network = Model(
        inputs=[anchor_input, positive_input, negative_input], outputs=distances
    )


    #Custom training loop for the Siamese network
    #--------------------------------------------

    class SiameseModel(Model):
        """The Siamese Network model with a custom training and testing loops.

        Computes the triplet loss using the three embeddings produced by the
        Siamese Network.

        The triplet loss is defined as:
        L(A, P, N) = max(‖f(A) - f(P)‖² - ‖f(A) - f(N)‖² + margin, 0)
        """

        def __init__(self, siamese_network, margin=0.5):
            super(SiameseModel, self).__init__()
            self.siamese_network = siamese_network
            self.margin = margin
            self.loss_tracker = metrics.Mean(name="loss")

        def call(self, inputs):
            return self.siamese_network(inputs)

        def train_step(self, data):
            # GradientTape is a context manager that records every operation that
            # you do inside. We are using it here to compute the loss so we can get
            # the gradients and apply them using the optimizer specified in
            # `compile()`.
            with tf.GradientTape() as tape:
                loss = self._compute_loss(data)

            # Storing the gradients of the loss function with respect to the
            # weights/parameters.
            gradients = tape.gradient(loss, self.siamese_network.trainable_weights)

            # Applying the gradients on the model using the specified optimizer
            self.optimizer.apply_gradients(
                zip(gradients, self.siamese_network.trainable_weights)
            )

            # Let's update and return the training loss metric.
            self.loss_tracker.update_state(loss)
            return {"loss": self.loss_tracker.result()}

        def test_step(self, data):
            loss = self._compute_loss(data)

            # Let's update and return the loss metric.
            self.loss_tracker.update_state(loss)
            return {"loss": self.loss_tracker.result()}

        def _compute_loss(self, data):
            # The output of the network is a tuple containing the distances
            # between the anchor and the positive example, and the anchor and
            # the negative example.
            ap_distance, an_distance = self.siamese_network(data)

            # Computing the Triplet Loss by subtracting both distances and
            # making sure we don't get a negative value.
            loss = ap_distance - an_distance
            loss = tf.maximum(loss + self.margin, 0.0)
            return loss

        @property
        def metrics(self):
            # We need to list our metrics here so the `reset_states()` can be
            # called automatically.
            return [self.loss_tracker]

    #setting up callbacks that get triggered at the end of each epoch

    plot_loss_1 = PlotLossesKerasTF()

    early_stop = EarlyStopping(monitor='val_loss',
                            patience=5,
                            restore_best_weights=True,
                            mode='min')
    #def scheduler(epoch, lr):
    #   if epoch < self.LR_exp_dec_when:
    #        return lr
    #    else:
    #        return lr * tf.math.exp(-0.1)
    #lr_callback = tf.keras.callbacks.LearningRateScheduler(scheduler)


    save_to = PROJECT_FOLDER+"models/" +prefix + backbone +'_LR'+str(learning_rate) + '_'+'{epoch:02d}-{val_loss:.2f}.hdf5'
    csv_logger = CSVLogger(PROJECT_FOLDER+"models/" +prefix+ backbone +'_LR'+str(learning_rate) +'.log')
        
    callbacks = [
        ModelCheckpoint(save_to, save_weights_only=True,save_freq='epoch',verbose=1),
        csv_logger,
        early_stop, 
        plot_loss_1,
        keras.callbacks.ReduceLROnPlateau(patience=2, verbose=1,cooldown=4),
        #lr_callback
        ]

    siamese_model = SiameseModel(siamese_network)
    siamese_model.compile(optimizer=optimizers.Adam(learning_rate))
    siamese_model.built = True

    if checkpoint_file != '' :
        siamese_model.load_weights(checkpoint_file)
        print('model checkpoint file loaded: ' + checkpoint_file)

    if continue_training:
        siamese_model.fit(train_dataset, epochs=epochs, validation_data=val_dataset,callbacks=callbacks,verbose=1)


    return base_cnn

