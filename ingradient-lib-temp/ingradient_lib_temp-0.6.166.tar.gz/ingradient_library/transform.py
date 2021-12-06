from ingradient_library.patch_transform import *
from ingradient_library.preprocessing import Resampling

class Transform(object):
    def __init__(self, transforms, probs):
        self.probs = probs
        self.transforms = transforms
        self.type_img_transformer = [Batch_Gaussian_Noise, Batch_Gaussian_Blur_3D, Batch_Contrast, Batch_Brightness, Batch_GammaTransform, Batch_Low_Resolution]
        self.type_img_seg_transformer = [Batch_Affine_3D, Batch_Mirroring]
        self.type_resampling = [Resampling]
        self.img_transformer = []
        self.img_seg_transformer = []
        self.resampling = []
        self.img_transformer_prob = []
        self.img_seg_transformer_prob = []

        for transform, prob in zip(self.transforms, probs):
            if type(transform) in self.type_img_transformer:
                self.img_transformer.append(transform)
                self.img_transformer_prob.append(prob)
            elif type(transform) in self.type_img_seg_transformer:
                self.img_seg_transformer.append(transform)
                self.img_seg_transformer_prob.append(prob)
            elif type(transform) in self.type_resampling:
                if prob != 1:
                    raise ValueError ("The probablity of Resampling msut be 1.0")
                self.resampling.append(transform)
    

    def __call__(self, images, seg, info):
        for i in range(len(self.resampling)):
            images = self.resampling[i](images, info, mode = 'x')
            seg = self.resampling[i](seg, info, mode = 'y')

        for i in range(len(self.img_transformer)):
            current_prob = self.img_transformer_prob[i]
            if np.random.uniform(0, 1) < current_prob:
                images = self.img_transformer[i](images)
    
        for i in range(len(self.img_seg_transformer)):
            current_prob = self.img_seg_transformer_prob[i]
            if np.random.uniform(0, 1) < current_prob:
                if isinstance(self.img_seg_transformer[i], Batch_Affine_3D):
                    self.img_seg_transformer[i].get_matrices_and_coords(images)
                
                elif isinstance(self.img_seg_transformer[i], Batch_Mirroring):
                    self.img_seg_transformer[i].get_mirror_axis()
                images = self.img_seg_transformer[i](images)
                seg = self.img_seg_transformer[i](seg)


        return images, seg