from PIL import Image
import random 
import os
from glob import glob
import numpy as np
from skimage import exposure
from skimage.exposure import match_histograms

def hist_match(source, template):
    """
    Adjust the pixel values of a grayscale image such that its histogram
    matches that of a target image

    Arguments:
    -----------
        source: np.ndarray
            Image to transform; the histogram is computed over the flattened
            array
        template: np.ndarray
            Template image; can have different dimensions to source
    Returns:
    -----------
        matched: np.ndarray
            The transformed output image
    """

    oldshape = source.shape
    source = source.ravel()
    template = template.ravel()

    # get the set of unique pixel values and their corresponding indices and
    # counts
    s_values, bin_idx, s_counts = np.unique(source, return_inverse=True,
                                            return_counts=True)
    t_values, t_counts = np.unique(template, return_counts=True)

    # take the cumsum of the counts and normalize by the number of pixels to
    # get the empirical cumulative distribution functions for the source and
    # template images (maps pixel value --> quantile)
    s_quantiles = np.cumsum(s_counts).astype(np.float64)
    s_quantiles /= s_quantiles[-1]
    t_quantiles = np.cumsum(t_counts).astype(np.float64)
    t_quantiles /= t_quantiles[-1]

    # interpolate linearly to find the pixel values in the template image
    # that correspond most closely to the quantiles in the source image
    interp_t_values = np.interp(s_quantiles, t_quantiles, t_values)

    return interp_t_values[bin_idx].reshape(oldshape)

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

    
    path_one_img  = "/home/webern/idsair_public/data/frame_images_ina/test/img"
    path_one_mask  = "/home/webern/idsair_public/data/frame_images_ina/test/mask"
    path_two_img  = "/home/webern/idsair_public/data/mean_images_ina/test/img"
    path_two_mask  = "/home/webern/idsair_public/data/mean_images_ina/test/mask"
    path_three_img  = "/home/webern/idsair_public/data/mean_images_julian/test/img"
    path_three_mask  = "/home/webern/idsair_public/data/mean_images_julian/test/mask"
    path_save_img = '/home/webern/idsair_public/data/interpolated_images/test/img/'
    path_save_mask = '/home/webern/idsair_public/data/interpolated_images/test/mask/'
    list_path_images = [ path_one_img
                       , path_two_img
                       , path_three_img
                       ]
    list_key_images = [ "*.png"
                      , "*.png"
                      , "*.png"
                      ]
    list_path_mask = [ path_one_mask
                     , path_two_mask
                     , path_three_mask
                     ]
    list_key_masks = [ "*.png"
                     , "*.png"
                     , "*.png"
                     ]
    number_folders = len(list_path_images)
    path_images = []
    path_segs = []
    for index_folder in range(number_folders):
        images = sorted(glob(os.path.join(list_path_images[index_folder], list_key_images[index_folder])))
        segs = sorted(glob(os.path.join(list_path_mask[index_folder], list_key_masks[index_folder])))
        num_total = len(images)
        for i in range(num_total):
            path_images.append(images[i])
            path_segs.append(segs[i])
            
    
    number_files = len(path_images)
    for i in range(70):
        number_one = random.randint(0,number_files-1)
        number_two = random.randint(0,number_files-1)
        alpha = random.uniform(0.2, 0.8)
        path_image_one = path_images[number_one]
        path_image_two = path_images[number_two]
        path_mask_one = path_segs[number_one]
        path_mask_two = path_segs[number_two]
        image_interpolation( path_image_one
                           , path_image_two
                           , path_mask_one
                           , path_mask_two
                           , alpha
                           , i
                           , path_save_img
                           , path_save_mask
                           )
        
    