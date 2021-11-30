import os
from ingradient_library.nnunet_3D_run import *
from ingradient_library.inference import Inference

LOAD_PATH = '/home/ubuntu/ingradient_lib_test'
SAVE_MODEL_PATH = '/home/ubuntu/model_state_dict'
patch_size = (40, 56, 40)
batch_size = 8
n_classes = 3
n_modalities = 1
GPU_DEVICE_INDEX = 0
SAVE_RESULT_PATH ='/home/ubuntu/result_file'
MODEL_LOAD = os.path.join(SAVE_MODEL_PATH,'epoch50_model_state_dict.pkl' )

narrow_inference_run(LOAD_PATH, MODEL_LOAD, SAVE_RESULT_PATH, GPU_DEVICE_INDEX, patch_size, n_classes, n_modalities)
#nnunet_3D_run_narrow(LOAD_PATH, SAVE_MODEL_PATH, GPU_DEVICE_INDEX, patch_size, batch_size, n_classes, n_modalities)