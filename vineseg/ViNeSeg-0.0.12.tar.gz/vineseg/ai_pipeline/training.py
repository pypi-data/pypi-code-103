import torch
import os.path
import json
import argparse
from pathlib import Path
from monai_models import get_model
from DataLoader import DataReader
from framework_bench import train, predict
from add_channels import channelProcessingInput, channelProcessingOutput
from preprocessing_augmentation import ( preprocessing
                                       , augmentation
                                       , convert_to_tensor
                                       )
from postprocessing import postprocessing
from monai.losses import DiceLoss, FocalLoss, TverskyLoss, DiceCELoss  
from monai.metrics import DiceMetric
from monai.utils import progress_bar
from monai.transforms import Compose
from torchcontrib.optim import SWA
from util import save_metrics

def prepare_recordings( recordings
                      , channel_types_input
                      , channel_types_output
                      ):
    prepared_data = [ { "img": channelProcessingInput(recordings[i].image, channel_types_input)
                      , "seg": channelProcessingOutput(recordings[i].label, channel_types_output)
                      } for i in range(len(recordings))
                    ]
    return prepared_data

def get_optimizer( optimizer_name
                 , model
                 , learning_rate
                 , weight_decay
                 ):
    if optimizer_name == "Adam":
        opt = torch.optim.Adam( model.parameters()
                              , learning_rate
                              )
    if optimizer_name == "AdamW":
        opt = torch.optim.AdamW( model.parameters()
                               , lr = learning_rate
                               , weight_decay = weight_decay
                               )
    return opt

def get_metrics(list_metric_names): 
    if "Dice Metric" in list_metric_names:
        metric = DiceMetric( include_background = True
                           , reduction = "mean"
                           )
    return metric

def get_loss_function(loss_name):
    if loss_name == "Dice loss":
        loss_function = DiceLoss( sigmoid = True
                                , squared_pred = True
                                , jaccard = True
                                , reduction = "mean"
                                )
    if loss_name == "Focal loss":
        loss_function = FocalLoss( to_onehot_y = True)
    if loss_name == "Tversky loss":
        loss_function = TverskyLoss( sigmoid = True
                                   , reduction = "mean"
                                   )
    if loss_name == "Dice focal loss":
        loss_function = DiceLoss( sigmoid = True
                                , squared_pred = True
                                , jaccard = True
                                , reduction = "mean"
                                )
    if loss_name == "Dice CE loss":
        loss_function = DiceCELoss(sigmoid = True)
    return loss_function
    
parser = argparse.ArgumentParser(description='Prediction for Neuron segmentation.')
parser.add_argument("--path_config_file", help="Path to config file.")
args = parser.parse_args()
path_config_file = args.path_config_file
with open(path_config_file) as config_file:
    config = json.load(config_file)
#TODO: copy dconfig file in experiment folder
#load model with settings
path_load_model = config["path loading model"]
model_type = config["model type"]
path_training_image_folder = config["paths training image folder"]
path_training_masks_folder = config["paths training masks folder"]
path_val_image_folder = config["paths val image folder"]
path_val_masks_folder = config["paths val masks folder"]
input_channels = config["number input channel"]
output_channels = config["number output channel"]
image_size = config["ROI training"]

#set hyperparameters and starting point for training
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") 
loss_name = config["loss function"]
metric_name = config["metrics"]
optimizer_name = config["optimizer"]
validation_intervall = config["validation intervall"]
epochs = config["epochs"]
batch_size = config["batch size"]
learning_rate = config["learning rate"]
weight_decay = config["weight decay"]
path_save_folder =  config["path save model"]
path_logging_results = config["logging training results"]

#parameters for preprocessing the images and data augmentation

#log hyperparameter of experiment
swa_model = None
model = get_model( model_type
                 , input_channels
                 , output_channels
                 , device
                 , image_size
                 )
if path_load_model != None:
    swa_model = torch.optim.swa_utils.AveragedModel(model)
    model.load_state_dict(torch.load(path_load_model + "/trained_weights/trained_weights.pth", map_location = device), strict = False)
    swa_model.load_state_dict(torch.load(path_load_model + "/trained_weights_swa/trained_weights.pth", map_location = device), strict = True)
#specify on which data you want to train
channel_types_input = config["channel types input"]
channel_types_output = config["channel types output"]
preprocessing_steps = config["preprocessing steps"]
postprocessing_steps = config["postprocessing"]
augmentation_steps = config["augmentation steps"]
augementation_probability = config["augmentation probability"]
ROI_training = config["ROI training"]

# create files. Target directories should not exist.
working_dir = path_save_folder
#create folders with summary and trained weights
Path(working_dir).mkdir(parents = True, exist_ok = False)
with open(working_dir + "/Experiment_parameter.json", 'a') as File: 
    json.dump(config, File, indent = 2)

Path(working_dir + "/trained_weights").mkdir(parents = True, exist_ok = False)
Path(working_dir + "/trained_weights_swa").mkdir(parents = True, exist_ok = False)

list_preprocessing_steps = preprocessing(preprocessing_steps)  
list_augmentations_steps = augmentation( augmentation_steps
                                       , ROI_training
                                       , augementation_probability
                                       )
list_to_tensor = convert_to_tensor()
trans_train = Compose(list_preprocessing_steps + list_augmentations_steps + list_to_tensor)
trans_val = Compose(list_preprocessing_steps + list_to_tensor)
postprocessing_steps = postprocessing(postprocessing_steps)

#model.train()
#First step: pretraining on public available dataset from dsb2018. Goal: learn general image structures
#Second step: Train on interpolated images of IDSAIR datasets. Goal: With this method we can generate more data with more
#complicated structures
#Third step: Make a short training on IDSAIR datas.

loss_function = get_loss_function(loss_name)
metric = get_metrics(metric_name)
opt = get_optimizer( optimizer_name
                   , model
                   , learning_rate
                   , weight_decay
                   )


train_recordings, _ = DataReader( path_training_image_folder
                                , path_training_masks_folder
                                , 0
                                )
_ , val_recordings = DataReader( path_val_image_folder
                               , path_val_masks_folder
                               , 1
                               )
print(channel_types_input)
print(channel_types_output)
data_train = prepare_recordings( train_recordings
                               , channel_types_input
                               , channel_types_output
                               )
data_val = prepare_recordings( train_recordings
                             , channel_types_input
                             , channel_types_output
                             )
print(trans_train)
print(trans_val)
model, swa_model, loss_function, opt = train( model
                                            , swa_model
                                            , data_train
                                            , trans_train
                                            , data_val
                                            , trans_val
                                            , epochs
                                            , batch_size
                                            , validation_intervall
                                            , loss_function
                                            , opt
                                            , metric
                                            , postprocessing_steps
                                            , device
                                            )
torch.save(model.state_dict(), working_dir + "/trained_weights/" + "trained_weights.pth")
if swa_model != None:
    torch.save(swa_model.state_dict(), working_dir + "/trained_weights_swa/" + "trained_weights.pth")
"""
model.eval()
swa_model.eval()
prediciton_data  = { "path images": ['/home/webern/idsair_public/data/mean_images_ina/test/img'
                                    , '/home/webern/idsair_public/data/mean_images_julian/test/img'
                                    , '/home/webern/idsair_public/data/frame_images_ina/test/img'
                                    ]
                    , "path masks": ['/home/webern/idsair_public/data/mean_images_ina/test/mask'
                                    , '/home/webern/idsair_public/data/mean_images_julian/test/mask'
                                    , '/home/webern/idsair_public/data/frame_images_ina/test/mask'
                                    ]
                    , "ROI validation": 512
                    }
train_recordings, val_recordings = DataReader( prediciton_data["path images"]
                                             , prediciton_data["path masks"]
                                             , 1
                                             )
data_val = [ { "img": channelProcessingInput(val_recordings[i].image, channelManipulationInput)
             , "seg": channelProcessingOutput(val_recordings[i].label, channelManipulationOutput)
             } for i in range(len(val_recordings))
            ]
list_data_names = [val_recordings[i].name for i in range(len(val_recordings))]
image_size = prediciton_data["ROI validation"]
dict_predictions_default, dict_metrics_default = predict( model 
                                                        , data_val
                                                        , trans_val
                                                        , list_data_names
                                                        , metric
                                                        , image_size
                                                        , postprocessing_steps
                                                        , device
                                                        )
dict_predictions_swa, dict_metrics_swa = predict( swa_model
                                                , data_val
                                                , trans_val
                                                , list_data_names
                                                , metric
                                                , image_size
                                                , postprocessing_steps
                                                , device
                                                )
experiment_parameter["swa"] = "no"
save_metrics(experiment_parameter, dict_metrics_default, global_result_file)
experiment_parameter["swa"] = "yes"
save_metrics(experiment_parameter, dict_metrics_swa, global_result_file)
#add experiment id if pretraining before
#after training only interested in metric, if we need prediction execute script prediction
"""