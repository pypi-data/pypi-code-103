import numpy as np
import six
import SimpleITK as sitk
from sklearn.decomposition import PCA
from radiomics import featureextractor

def extract_radiomic_features(sub_img, sub_mask, category="all", window_size=2, PCs=None):
    """
    Extract pre-defined radiomic features, you can select a category of features or use all features
    Args:
        sub_img: Numpy array. Rectangle image contains nodule
        sub_mask: Numpy array. Same size as sub_img with binary values, 1 for tumor area and 0 for background
        category: Str. The category of radiomic features. Choices are: "first-order", "texture", "PCA"
        window_size: Int. Size of sliding window when extract radiomic features for each pixel. window_size=2 for a 5x5 window
        PCs: Int, Number of PC when using category "PCA"
    Returns:
        features: Numpy array. A p x n matrix, p is the number of pixels of tumor, n is the number of radiomic features
    """
    features = dict()
    features['first'] = []
    features['shape'] = []
    features['glcm'] = []
    features['gldm'] = []
    features['glrlm'] = []
    features['glszm'] = []
    features['ngtdm'] = []
    for p in range(len(sub_img)):
        for q in range(len(sub_img[0])):
            if sub_mask[p][q] == 1:
                mask = np.copy(sub_img)
                mask[:, :] = 0
                mask[p - window_size:p + window_size + 1, q - window_size:q + window_size + 1] = 1
                img_ex = sitk.GetImageFromArray([sub_img])
                mask_ex = sitk.GetImageFromArray([mask])
                extractor = featureextractor.RadiomicsFeatureExtractor()
                radio_result = extractor.execute(img_ex, mask_ex)
                first_features_temp = []
                shape_features_temp = []
                glcm_features_temp = []
                gldm_features_temp = []
                glrlm_features_temp = []
                glszm_features_temp = []
                ngtdm_features_temp = []
                for key, val in six.iteritems(radio_result):
                    if key.startswith('original_firstorder'):
                        first_features_temp.append(val)
                    elif key.startswith('original_shape'):
                        shape_features_temp.append(val)
                    elif key.startswith('original_glcm'):
                        glcm_features_temp.append(val)
                    elif key.startswith('original_gldm'):
                        gldm_features_temp.append(val)
                    elif key.startswith('original_glrlm'):
                        glrlm_features_temp.append(val)
                    elif key.startswith('original_glszm'):
                        glszm_features_temp.append(val)
                    elif key.startswith('original_ngtdm'):
                        ngtdm_features_temp.append(val)
                    else:
                        pass
                features['first'].append(first_features_temp)
                features['shape'].append(shape_features_temp)
                features['glcm'].append(glcm_features_temp)
                features['gldm'].append(gldm_features_temp)
                features['glrlm'].append(glrlm_features_temp)
                features['glszm'].append(glszm_features_temp)
                features['ngtdm'].append(ngtdm_features_temp)
    if category == 'all':
        features = np.hstack((features['first'], features['shape'], features['glcm'], features['gldm'], features['glrlm'], features['glszm'], features['ngtdm']))
    elif category == 'first-order':
        features = features['first']
    elif category == 'texture':
        features = np.hstack((features['glcm'], features['gldm'], features['glrlm'], features['glszm'], features['ngtdm']))
    elif category == 'PCA':
        features = np.hstack((features['first'], features['shape'], features['glcm'], features['gldm'], features['glrlm'], features['glszm'], features['ngtdm']))
        features = PCA(n_components = PCs).fit_transform(features)
    else:
        raise RuntimeError('inputError')

    return features
