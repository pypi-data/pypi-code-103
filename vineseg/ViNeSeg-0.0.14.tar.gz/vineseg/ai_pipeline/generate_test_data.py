from PIL import Image
import random 
import os
from glob import glob
import numpy as np
from monai.data import ArrayDataset, create_test_image_2d


def image_interpolation ( path_image_one
                        , path_image_two
                        , path_mask_one
                        , path_mask_two
                        , alpha
                        , index_number
                        , path_save_img
                        , path_save_mask
                        ):
    im1 = Image.open(path_image_one)
    im2 = Image.open(path_image_two)
    im1 = np.asarray(im1).astype(float)
    im2 = np.asarray(im2).astype(float)
    im1 -= im1.mean()
    im1 /= im1.std()
    im2 -= im2.mean()
    im2 /= im2.std()
    im1 = exposure.rescale_intensity(im1, out_range=(0,1))
    im2 = exposure.rescale_intensity(im2, out_range=(0,1))
    im1 = exposure.equalize_adapthist(im1, clip_limit = 0.03)
    im2 = exposure.equalize_adapthist(im2, clip_limit = 0.03)
    im2 = hist_match(im2, im1)
    #im2 = match_histograms(im2, im1)
    im1 = (255*im1).astype(np.uint8)
    im2 = (255*im2).astype(np.uint8)
    im2 = Image.fromarray(im2)
    im1 = Image.fromarray(im1)
    mask1 = Image.open(path_mask_one)
    mask2 = Image.open(path_mask_two)
    interpolated_image = Image.blend(im1, im2, alpha)
    interpolated_mask = Image.blend(mask1, mask2, alpha)
    thresh = 0
    fn = lambda x : 255 if x > thresh else 0
    interpolated_mask = interpolated_mask.convert('L').point(fn, mode='1')
    current_path = os.getcwd()
    filename_image = "interpolated_image-%d.png" % index_number
    filename_mask = "interpolated_mask-%d.png" % index_number
    interpolated_image.save(path_save_img + filename_image)
    interpolated_mask.save(path_save_mask + filename_mask)
   


if __name__ == "__main__":

    for i in range(50):
        im, seg = create_test_image_2d(512, 512, num_seg_classes=1, num_objs = 60,  noise_max=0.1)
        im = Image.fromarray(255*im)
        im = im.convert('L')
        im.save(os.path.join("/home/webern/idsair_public/data/synthetic_data/test/img", f"img{i:d}.png"))
        Image.fromarray(255*seg.astype("uint8")).save(os.path.join("/home/webern/idsair_public/data/synthetic_data/test/mask", f"seg{i:d}.png"))
    
   