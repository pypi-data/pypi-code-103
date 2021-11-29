from .basic_crop import FaceCropper


def crop_image(img, resolution, landmark_predictor_path, if_mirror_padding=False, check_resolution=False, upper_limit_of_black_region_ratio=1.):
    # img is pil or path
    face_cropper = FaceCropper(landmark_predictor_path, resolution, if_mirror_padding, check_resolution, upper_limit_of_black_region_ratio)
    cropped_img = face_cropper.crop_face_from_image(img)
    return cropped_img

def crop_image_from_path(img_path, resolution, landmark_predictor_path, if_mirror_padding=False, check_resolution=False, upper_limit_of_black_region_ratio=1.):
    face_cropper = FaceCropper(landmark_predictor_path, resolution, if_mirror_padding, check_resolution, upper_limit_of_black_region_ratio)
    cropped_img = face_cropper.crop_face_from_path(img)
    return cropped_img