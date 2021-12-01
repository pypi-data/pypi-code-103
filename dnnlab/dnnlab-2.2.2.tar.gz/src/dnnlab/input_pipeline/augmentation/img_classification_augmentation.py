# Copyright 2019 Tobias Höfer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

""" Tool "imgaug" is used for data/image augmentation
see https://imgaug.readthedocs.io/en/latest/source/installation.html for reference

API: https://imgaug.readthedocs.io/en/latest/source/api_imgaug.html

Install:
Prerequisites: 
- pip install opencv-python-headless --upgrade
- pip install opencv-contrib-python-headless --upgrade

- Conda
    - conda config --add channels conda-forge
    - conda install imgaug
    - pip install imagecorruptions
- Pip
    - pip install imgaug
    - pip install imagecorruptions
"""

from imgaug import augmenters as iaa
import imgaug as ia
import numpy as np
import tensorflow as tf
import random



class ImageClassificationAugmentation:
    """ Example usage of ImageClassificationAugmentation

    1) create ImageClassificationAugmentation object
    ica = dnnlab.input_pipeline.augmentation.img_classification_augmentation.ImageClassificationAugmentation()

    2) create list of wanted augmentations. You can choose betwenn rotate, shift in x direction, shift in y direction
       These augmentations need a pair of 2 values in a shape 
       (max negative value, max positive value) from which the values for each augmentation step are randomly selected.
       The augmentations noise and dropout need just one single value because their ranges are from 0 to value.
    aug_list = [("rotate", (-10,10)), ("shiftx", (-20, 20)), ("shifty", (-20, 20)), ("noise", 0.01), ("dropout", 0.2)]

    3) setup augmentation operations with augmentation list
    ica.setup(aug_list)

    4) augment dataset 
    training_data = ica.augment_data(training_data, batch_size=BATCH_SIZE, increase_dataset=False, 
                                    buffer_size=BUFFER_SIZE, seed=SEED,
                                    prefetching=True, cache=True, class_factors=[2, 0, 8, 9, 4])
    """
    def __init__(self):
        self.augmenters = iaa.OneOf([])  # imgaug.augmenters.meta
    
    
    def add_rotation(self, angles):
        """ add Rotation Augmentation operation to list of augmenters

        Args:
            angles (pair): pair of max negative angle and max positive angle
        """
        rot_op = iaa.Rotate(angles, name="Rotate")
        self.augmenters.add(rot_op)


    def add_shift_x(self, pixels):
        """ add Shift-X Augmentation operation to list of augmenters

        Args:
            pixels (pair): pair of max negative pixel and max positive pixel
        """
        shift_op = iaa.TranslateX(px=pixels, name="ShiftX")
        self.augmenters.add(shift_op)


    def add_shift_y(self, pixels):
        """ add Shift-Y Augmentation operation to list of augmenters

        Args:
            pixels (pair): pair of max negative pixel and max positive pixel
        """
        shift_op = iaa.TranslateY(px=pixels, name="ShiftY")
        self.augmenters.add(shift_op)


    def add_noise(self, scale):
        """ add AdditiveGaussianNoise Augmentation operation to list of augmenters

        Args:
            scale (int): Standard deviation of the normal distribution that generates the noise. 
                         Has to be a value between 0 and 1.
        """
        noise_op = iaa.AdditiveGaussianNoise(scale=(0, scale*255), name="Noise")
        self.augmenters.add(noise_op)


    def add_dropout(self, percent):
        """ add Dropout Augmentation operation to list of augmenters

        Args:
            percent (int): drop percent of all pixels in the image (i.e. convert them to black pixels).
                           Has to be a value between 0 and 1.
        """
        dropout_op = iaa.Dropout(p=(0, percent), name="Dropout")
        self.augmenters.add(dropout_op)


    def setup(self, op_pairs):
        """ setup choosen augmentation operations with parameters.

        Args:
            op_pairs [(op_name (string), op_values (int, int) or (int)), (op_name (string), op_values (int, int) or (int))]
        """
        if op_pairs is None:
            self.augmenters.add(iaa.Identity())
        else:
            for op in op_pairs:
                name = op[0]
                values = op[1]

                if name == "rotate":
                    self.add_rotation(angles=values)
                if name == "shiftx":
                    self.add_shift_x(pixels=values)
                if name == "shifty":
                    self.add_shift_y(pixels=values)
                if name == "noise":
                    self.add_noise(scale=values)
                if name == "dropout":
                    self.add_dropout(percent=values)


    def augment_data(self, dataset,
                     buffer_size,
                     seed,
                     batch_size,
                     increase_dataset=False,
                     prefetching=True,
                     cache=True, 
                     class_factors=None):
        """ perform augmetation on a dataset.
        Choose between class unbalanced augmentation or 
        class balanced augmentation with weighted class factors to handle label imbalance.

        Args:
            dataset (tf.dataset): tf.Dataset with shape (None, width, height, depth)
            buffer_size (int): representing the maximum number of elements that will be buffered when prefetching.
            seed (int): representing the random seed that will be used to create the distribution
            batch_size (int): batch size
            increase_dataset (bool): determine if origin dataset and augmented dataset are concatenated
            prefetching (bool): determine if prefetching is On or Off
            cache (bool): determine if cache is On or Off
            class_factors (list(int)): list of class factors for weighting number of additional augmented samples
        """
        if class_factors is None:
            return self.augment_unbalanced(dataset=dataset,
                     buffer_size=buffer_size,
                     seed=seed,
                     batch_size=batch_size,
                     increase_dataset=increase_dataset,
                     prefetching=prefetching,
                     cache=cache)
        else:
            return self.augment_balanced(dataset=dataset,
                     buffer_size=buffer_size,
                     seed=seed,
                     batch_size=batch_size,
                     increase_dataset=increase_dataset,
                     prefetching=prefetching,
                     cache=cache,
                     class_factors=class_factors)


    def augment_balanced(self, dataset,
                     buffer_size,
                     seed,
                     batch_size,
                     increase_dataset=False,
                     prefetching=True,
                     cache=True,
                     class_factors=None):
        """ perform augmetation on a dataset with weighted class factors to handle label imbalance.

        Args:
            dataset (tf.dataset): tf.Dataset with shape (None, width, height, depth)
            buffer_size (int): representing the maximum number of elements that will be buffered when prefetching.
            seed (int): representing the random seed that will be used to create the distribution
            batch_size (int): batch size
            increase_dataset (bool): determine if origin dataset and augmented dataset are concatenated
            prefetching (bool): determine if prefetching is On or Off
            cache (bool): determine if cache is On or Off
            class_factors (list(int)): list of class factors for weighting number of additional augmented samples
        """
        class_factors = np.asarray(class_factors) 
        i = 0 # index for iterating over all batches of origin dataset

        batch_stacked_aug_imgs=None
        batch_stacked_aug_labels=None

        for elements in dataset:
            images = elements[0].numpy()
            labels = elements[1].numpy()

            images_shape = images.shape

            orig_batch_size = images.shape[0]

            if class_factors is not None:
                
                # index for iterating over one batch of origin dataset
                for b in range(orig_batch_size):  
                    image = images[b]
                    label = labels[b]      

                    # find factors for true labels
                    # np.where returns tuple for N-d case 
                    # which is not needed here because label is one-hot vector
                    label_indices = np.where(label > 0)[0] 
                    increase_factors = class_factors[label_indices]
                    sum_factors = np.sum(increase_factors)

                    # only apply augmentation when class_factors have a sum > 0
                    # -> not weighted classes will not be augmented
                    # therefore, samples with only one class which have a factor of 0 will not be considered
                    if sum_factors > 0:
                        # choose randomly the indices of applied augmentation techniques
                        # augmenters.meta.OneOf only selects one operation
                        # but due to balancing we want to apply a certain number of operations
                        len_augmenters = len(self.augmenters.get_children_lists()[0])
                        rand_aug_indices = random.choices(range(0, len_augmenters), k=sum_factors)

                        a = 0 # index for iterating over rand_aug_indices
                        for aug_index in rand_aug_indices:
                            # get list of register augment operations of augmenters.meta.Augmenter
                            # according to aug_index choose the randomly selected operation to augment the image
                            aug_img = self.augmenters.get_children_lists()[0][aug_index].augment(image=image)

                            # expand dimension to be stack them into a 4-D and 2-D array
                            aug_img = np.expand_dims(aug_img, axis=0)
                            aug_label = np.expand_dims(label, axis=0)

                            if batch_stacked_aug_imgs is None and batch_stacked_aug_labels is None:
                                batch_stacked_aug_imgs = aug_img
                                batch_stacked_aug_labels = aug_label
                            else: 
                                batch_stacked_aug_imgs = np.vstack((batch_stacked_aug_imgs, aug_img))
                                batch_stacked_aug_labels = np.vstack((batch_stacked_aug_labels, aug_label))

                            a+=1 # udpate index to iterate over rand_aug_indices
                
                i+=1 # update index to iterate over all batches

        # create tf.data.Dataset from numpy-arrays
        aug_dataset = tf.data.Dataset.from_tensor_slices((batch_stacked_aug_imgs, batch_stacked_aug_labels))
        aug_dataset = aug_dataset.batch(batch_size)

        # concat origin dataset and augmented dataset if increase_dataset=True
        # else just use aug_dataset
        if increase_dataset:
            result_dataset = dataset.concatenate(aug_dataset)
        else:
            result_dataset = aug_dataset

        result_dataset = result_dataset.shuffle(buffer_size, seed=seed)

        # Prefetching
        if prefetching:
            result_dataset = result_dataset.prefetch(
                tf.data.experimental.AUTOTUNE)
        # Cache
        if cache:
            # Apply time consuming operations before cache.
            result_dataset = result_dataset.cache()

        return result_dataset

    
    def augment_unbalanced(self,
                     dataset,
                     buffer_size,
                     seed,
                     batch_size,
                     increase_dataset=False,
                     prefetching=True,
                     cache=True):
        """ perform augmetation on a dataset
        Args:
            dataset (tf.dataset): tf.Dataset with shape (None, width, height, depth)
            buffer_size (int): representing the maximum number of elements that will be buffered when prefetching.
            seed (int): representing the random seed that will be used to create the distribution
            batch_size (int): batch size
            increase_dataset (bool): determine if origin dataset and augmented dataset are concatenated
            prefetching (bool): determine if prefetching is On or Off
            cache (bool): determine if cache is On or Off
        """
        i = 0 # index for stacking augmented images and labels
        for elements in dataset:
            images = elements[0].numpy()
            labels = elements[1].numpy()

            # augmetners.meta.OneOf randomly selects one registered augmentation operation
            aug_imgs = self.augmenters(images=images)

            if i==0: # first iteration to init array stack
                stacked_aug_imgs = aug_imgs
                stacked_aug_labels = labels
            else: # after first itreation stack (in batch dimension) aug_imgs and aug_labels
                stacked_aug_imgs = np.vstack((stacked_aug_imgs, aug_imgs))
                stacked_aug_labels = np.vstack((stacked_aug_labels, labels))
            
            i+=1 # update index

        # create tf.data.Dataset from numpy-arrays
        aug_dataset = tf.data.Dataset.from_tensor_slices((stacked_aug_imgs, stacked_aug_labels))
        aug_dataset = aug_dataset.batch(batch_size)

        # concat origin dataset and augmented dataset if increase_dataset=True
        # else just use aug_dataset
        if increase_dataset:
            result_dataset = dataset.concatenate(aug_dataset)
        else:
            result_dataset = aug_dataset

        result_dataset = result_dataset.shuffle(buffer_size, seed=seed)

        # Prefetching
        if prefetching:
            result_dataset = result_dataset.prefetch(
                tf.data.experimental.AUTOTUNE)
        # Cache
        if cache:
            # Apply time consuming operations before cache.
            result_dataset = result_dataset.cache()

        return result_dataset