import torch
import os.path
import json
import argparse
from pathlib import Path
from .monai_models import get_model
from .DataLoader import DataReader
from .framework_bench import train, predict
from .add_channels import channelProcessingInput, channelProcessingOutput
from .preprocessing_augmentation import ( preprocessing
                                       , augmentation
                                       , convert_to_tensor
                                       )
from .postprocessing import postprocessing
from monai.losses import DiceLoss, FocalLoss, TverskyLoss  
from monai.metrics import DiceMetric
from monai.utils import progress_bar
from monai.transforms import Compose
from torchcontrib.optim import SWA
from .util import save_as_image, convert_to_polygons_and_save

def pred_main(path, maximal_area_neuron_in_pixels=700, minimal_area_neuron_in_pixels=25):
    #load model with settings

    curr_path = os.path.dirname(__file__).replace("\\", "/")
    path_load_folder = curr_path.replace("ai_pipeline", "experiments/batch_unet3/")

    path_image_folder = [path]

    # works in this case but not generally
    path_masks = []
    #for p in path_image_folder:
    #    path_masks.append(p.replace("img", "mask"))

    if not os.path.exists(path.replace("img", "predictions/img")):
        os.makedirs(path.replace("img", "predictions/img"))

    path_predictions = path.replace("img", "predictions/")

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    image_size = 64 #should be the same as specified in experiment


    with open(path_load_folder + "Experiment_parameter.json") as File:
        dict_model_and_training = json.load(File)
        model_name = dict_model_and_training["model type"]
        input_channels = dict_model_and_training["number input channel"]
        output_channels = dict_model_and_training["number output channel"]
        image_size = dict_model_and_training.get('image_size_network', image_size)
        model = get_model(model_name
                          , input_channels
                          , output_channels
                          , device
                          , image_size
                          )
        swa_model = torch.optim.swa_utils.AveragedModel(model)
        path_model = path_load_folder + 'trained_weights/' + 'trained_weights.pth'
        path_swa_model = path_load_folder + 'trained_weights_swa/' + 'trained_weights.pth'
        model.load_state_dict(torch.load(path_model, map_location=device), strict=False)
        # swa_model.load_state_dict(torch.load(path_swa_model, map_location = device), strict=True) doesn't work in case of unet transfomer
        channelManipulationInput = dict_model_and_training["channel types input"]
        channelManipulationOutput = dict_model_and_training["channel types output"]

    metric = DiceMetric(include_background=True
                        , reduction="mean"
                        )
    _, val_recordings = DataReader(path_image_folder
                                   , path_masks
                                   , 1
                                   )
    data_val = [{"img": channelProcessingInput(val_recordings[i].image, channelManipulationInput)
                    , "seg": channelProcessingOutput(val_recordings[i].label, channelManipulationOutput)
                 } for i in range(len(val_recordings))
                ]
    list_preprocessing_steps = preprocessing(dict_model_and_training["preprocessing steps"])
    postprocessing_steps = postprocessing(dict_model_and_training["postprocessing"])
    list_to_tensor = convert_to_tensor()
    trans_val = Compose(list_preprocessing_steps + list_to_tensor)
    list_data_names = [val_recordings[i].name for i in range(len(val_recordings))]
    list_file_paths = [val_recordings[i].filePath for i in
                       range(len(val_recordings))]  # neeed such that json is compatible to labelme
    image_size = 512
    dict_predictions_default, dict_metrics_default = predict(model  # swa_model
                                                             , data_val
                                                             , trans_val
                                                             , list_data_names
                                                             , metric
                                                             , image_size
                                                             , postprocessing_steps
                                                             , device
                                                             )
    save_as_image(dict_predictions_default, path_predictions)
    convert_to_polygons_and_save(dict_predictions_default
                                 , list_file_paths
                                 , path_predictions
                                 , "json"
                                 , maximal_area_neuron_in_pixels
                                 , minimal_area_neuron_in_pixels
                                 )


"""
parser = argparse.ArgumentParser(description='Prediction for Neuron segmentation.')
parser.add_argument("--path_config_file", help="Path to config file.")
args = parser.parse_args()
path_config_file = args.path_config_file
with open(path_config_file) as config_file:
    config = json.load(config_file)
#load model with settings
path_load_folder = config["path_loading_weights_and_parameters"]
path_image_folder = config["paths_image_folder"]
path_masks = config["paths_masks_folder"]
path_predictions = config["path_save_predictions"]
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") 
image_size = 64 #should be the same as specified in experiment
with open(path_load_folder + "Experiment_parameter.json") as File:
    dict_model_and_training = json.load(File)
    model_name = dict_model_and_training["Model type"]
    input_channels = dict_model_and_training["number input channel"]
    output_channels = dict_model_and_training["number output channel"]
    image_size = dict_model_and_training.get('image_size_network', image_size)
    model = get_model( model_name
                     , input_channels
                     , output_channels
                     , device
                     , image_size
                     )
    swa_model = torch.optim.swa_utils.AveragedModel(model)
    path_model = path_load_folder + 'trained_weights/' + 'trained_weights.pth'
    path_swa_model = path_load_folder + 'trained_weights_swa/' + 'trained_weights.pth'
    model.load_state_dict(torch.load(path_model, map_location = device), strict=False)
    #swa_model.load_state_dict(torch.load(path_swa_model, map_location = device), strict=True) doesn't work in case of unet transfomer
    channelManipulationInput = dict_model_and_training["channel types input"]
    channelManipulationOutput = dict_model_and_training["channel types output"]

metric = DiceMetric( include_background = True
                   , reduction = "mean"
                   )
_, val_recordings = DataReader( path_image_folder
                              , path_masks
                              , 1
                              )
data_val = [ { "img": channelProcessingInput(val_recordings[i].image, channelManipulationInput)
             , "seg": channelProcessingOutput(val_recordings[i].label, channelManipulationOutput)
             } for i in range(len(val_recordings))
           ]
list_preprocessing_steps = preprocessing(dict_model_and_training["Preprocessing steps"])
postprocessing_steps = postprocessing(dict_model_and_training["Postprocessing"])  
list_to_tensor = convert_to_tensor()
trans_val = Compose(list_preprocessing_steps + list_to_tensor)
list_data_names = [val_recordings[i].name for i in range(len(val_recordings))]
list_file_paths = [val_recordings[i].filePath for i in range(len(val_recordings))] #neeed such that json is compatible to labelme
image_size = 512
dict_predictions_default, dict_metrics_default = predict( model #swa_model
                                                        , data_val
                                                        , trans_val
                                                        , list_data_names
                                                        , metric
                                                        , image_size
                                                        , postprocessing_steps
                                                        , device
                                                        )
save_as_image(dict_predictions_default, path_predictions)
convert_to_polygons_and_save(dict_predictions_default, list_file_paths, path_predictions, "json")
"""