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
# ==============================================================================

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


"""
Grad-CAM is a form of post-hoc attention, meaning that it is a method for producing heatmaps that is 
applied to an already-trained neural network after training is complete and the parameters are fixed. 
This is distinct from trainable attention, which involves learning how to produce attention maps (heatmaps) 
during training by learning particular parameters.
Grad-CAM does not require a particular CNN architecture because it is a generalization of CAM (class activation mapping).

In Grad-CAM, we weight the feature maps using “alpha values” that are calculated based on gradients. 
Therefore, Grad-CAM does not require a particular architecture, because we can calculate gradients through any kind 
of neural network layer we want. 
The output of Grad-CAM is a “class-discriminative localization map”, i.e. a heatmap where the hot part corresponds 
to a particular class:

        L^c_GradCAM in R^(u x v)    class-dicriminative localization map: width u, height v, class c

This localises the detected object to a region in the image.              
If there are 10 possible output classes, then for a particular input image, 
you can make 10 different Grad-CAM heatmaps, one heatmap for each class.

Grad-CAM is applied to a neural network that is done training. The weights of the neural network are fixed. 
We feed an image into the network to calculate the Grad-CAM heatmap for that image for a chosen class of interest.

Step 1: Compute Gradient
Step 2: Compute alpha values by Averaging Gradients
Step 3: Calculate final Grad-CAM heatmap

"""

class GradCam():
    """Implements GradCam which is an approach for model explainability which produces 
    a heatmap of which regions of an image contributed strongly towards the final prediction 
    Link to original paper: https://arxiv.org/pdf/1610.02391.pdf

    Attributes:
        model (keras.model): trained tf.keras model
        layerName (str): An optional CONV layerName of the model in case we want to visualize the heatmap of a specific layer of our CNN; 
                        otherwise, if a specific layer name is not provided, 
                        we will automatically infer on the final CONV/POOL layer of the model architecture.
    """

    def __init__(self, model, layerName=None):
        self.model = self.check_activation(model)
        self.layerName = layerName

        # if the layer name is None, find the target output layer
        if self.layerName is None:
            self.layerName = self.find_target_layer()
            print("TargetLayer: ", self.layerName)
        else:
            print("TargetLayer: ", self.layerName)

    
    def find_target_layer(self):
        """Attempt to find the (final) convolutional/pooling layer in the network
        by looping over the layers of the network in reverse order.

        Args:

        Returns:
            layerName (str): name of last layer which has a 4D output

        """
        for layer in reversed(self.model.layers):
            # check to see if the layer has a 4D output
            if len(layer.output.shape) == 4:
                return layer.name
        # otherwise, we could not find a 4D layer so GradCAM cannot be applied
        raise ValueError("Could not find a 4D layer. Cannot apply GradCAM.")


    def check_activation(self, model):
        """ Check which layer of the model applies the final
        activation (softmax/sigmoid, etc).
        This final activation needs to be skipped because GradCam
        operates on the "raw" network output instead of on probabilites.

        Args:
            model (tf.keras.model): trained model which should perform GradCAM
        
        Returns:
            model (tf.keras.model): same model which skips final activation
        """
        # if last activation is an own layer remove the layer
        if 'activation' in model.layers[-1].name:
            return tf.keras.Model(model.inputs, model.layers[-2].output)
        # if last layer has an activation function set it to None
        else: 
            model.layers[-1].activation = None
            return model

        
    def compute_heatmap(self, image, target_class_idx=None):
        """ Compute the GradCAM heatmap.

        Args:
            image: one single image sample of [1, H, W, D]
            target_class_idx (int): index of target class for which heatmap should be created
        
        Returns:
            heatmap (np.array): unscaled GradCAM heatmap with same shape as last 4D layer
        """
        # create a model that maps the input image to the activations A
        # of the last conv/pool layer as well as the output predictions y (before the final softmax/sigmoid, etc)
        grad_model = tf.keras.models.Model(
            inputs=[self.model.inputs], 
            outputs=[self.model.get_layer(self.layerName).output, self.model.output]
        )

        ### Step 1: compute gradient of the model output y^c w.r.t. to the feature map activations

        # compute the gradient of the top predicted class for the input image
        # w.r.t. the activations of the last 4D layer
        with tf.GradientTape() as tape:
            last_conv_layer_output, preds = grad_model(image) # (1, U, V, K), (1, C)
          
            # find target class index
            if target_class_idx is None:
                target_class_idx = tf.argmax(preds[0]) # (1, )

            class_channel = preds[:, target_class_idx] # (1, ), can be seen as "loss"
        
        # get gradient of the output neuron for the choosen target class
        # w.r.t the output feature map of the last conv layer
        grads = tape.gradient(class_channel, last_conv_layer_output) # (1, U, V, K)


        ### Step 2: compute alpha values by averaging the gradients

        # calculate a vector where each entry is the mean intensity of the gradient
        # over a specific feature map channel
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2)) # (K, )


        ### Step 3: Compute final heatmap

        last_conv_layer_output = last_conv_layer_output[0] # (U, V, K)

        # multiply each channel in the feature map array with the importance of this channel
        # and sum all the channels to obtain the heatmap class activation
        # this is exactly what a matrix multiplication does
        # @ is used in decorator syntax and for matrix multiplication.
        heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis] # (U, V, 1)
        heatmap = tf.squeeze(heatmap) # (U, V)

        # apply ReLU (tf.maximum) and normalize the heatmap between [0, 1]
        heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap) # (U, V)

        return heatmap.numpy()
    

    def save_and_display_gradcam(self, img, heatmap, label, cam_path="cam.jpg", alpha=0.4):
        """ Overlay original image and heatmap to get GradCAM image. This results in a plot
        of the original images next to the overlayed image.

        Args:
            img (np.array): original image (H, W, C)
            heatmap (np.array): unscaled heatmap (U, V)
            label (np.array): single or one-hot label of original image
            cam_path (str): path/filename to store the plotted image
            alpha (float): Default: 0.4; factor to weigth the overlayed heatmap

        Returns:

        """
        # rescale heatmap to values between [0, 255]
        heatmap = np.uint8(255 * heatmap)

        # create colormap
        jet = cm.get_cmap("jet")

        # only use RGB values of the colormap
        jet_colors = jet(np.arange(256))[:, :3]
        jet_heatmap = jet_colors[heatmap]

        # create an image with RGB colorized heatmap out of the colormap heatmap
        jet_heatmap = tf.keras.preprocessing.image.array_to_img(jet_heatmap)
        jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
        jet_heatmap = tf.keras.preprocessing.image.img_to_array(jet_heatmap)

        # superimpose the heatmap on original image
        superimposed_img = jet_heatmap * alpha + img
        superimposed_img = tf.keras.preprocessing.image.array_to_img(superimposed_img)


        # construct combined plot and save it
        plt.figure()
        plt.suptitle('Original vs GradCAM')
        plt.subplot(121)
        plt.title("Original Label: " + str(label))
        plt.imshow(tf.keras.preprocessing.image.img_to_array(img), cmap='gray')
        plt.subplot(122)
        plt.title("")
        plt.imshow(superimposed_img)
        plt.savefig(cam_path)
        plt.close()


    
    
    


    



