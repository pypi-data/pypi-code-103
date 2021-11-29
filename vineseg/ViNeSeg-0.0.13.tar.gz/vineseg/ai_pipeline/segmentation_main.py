import torch
import os.path
import json
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

"""preprocessing options for input
1. identity
2. clahe
3. nl_means
4. autolevel
5. gamma low
6. gamma high
7. rolling ball
8. adjust sigmoid
"""

#set hyperparameters and starting point for training
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") 
epochs = 1000
batch_size = 1
learning_rate = 1e-4
experiment_name = "pretraining_transformer_again4"
starting_experiment = None
path_save_folder =  "/home/webern/idsair_public/experiments/" + experiment_name + "/"
global_result_file = "/home/webern/idsair_public/experiments/"

#log hyperparameter of experiment
experiment_parameter = {}
experiment_parameter["experiment_name"] = experiment_name
experiment_parameter["starting_experiment"] = starting_experiment
experiment_parameter["epochs"] = epochs
experiment_parameter["batch size"] = batch_size
experiment_parameter["learning_rate"] = learning_rate
if starting_experiment is not None:
    path_load_folder = "/home/webern/idsair_public/experiments/" + starting_experiment + "/"
else:
    path_load_folder = None

swa_model = None
if path_load_folder != None:
    with open(path_load_folder + "Experiment_parameter.json") as File:
        dict_model_and_training = json.load(File)
    model_type = dict_model_and_training["Model type"]
    experiment_parameter["model type"] = model_type
    if model_type == "U-Net big":
        model = get_multiple_channel_UNet( dict_model_and_training["number input channel"]
                                         , dict_model_and_training["number output channel"]
                                         , device
                                          )
    if model_type == "SegResNet":
        model = get_multiple_channel_SegResNet( dict_model_and_training["number input channel"]
                                              , dict_model_and_training["number output channel"]
                                              , device
                                              )
    if model_type == "UNetTransformer":
        image_size = dict_model_and_training["ROI training"]
        model = get_multiple_channel_UNetTransformer( dict_model_and_training["number input channel"]
                                                    , dict_model_and_training["number output channel"]
                                                    , image_size
                                                    , device
                                                    )
    swa_model = torch.optim.swa_utils.AveragedModel(model)
    path_model = path_load_folder + 'trained_weights/' + 'trained_weights.pth'
    path_swa_model = path_load_folder + 'trained_weights_swa/' + 'trained_weights.pth'
    model.load_state_dict(torch.load(path_model, map_location = device), strict=False)
    swa_model.load_state_dict(torch.load(path_swa_model, map_location = device), strict=True)
    dict_model_and_training = { "ROI training": 64
                              , "ROI validation": 64
                              , "Augementation probability": 0.5
                              , "Preprocessing steps": ["ScaleIntensity"]
                              , "Augmentation steps": [ "SpatialCrop"
                                                      #, "GaussianNoise"
                                                      , "Rotate"
                                                      , "Flip"
                                                      , "Zoom"
                                                      , "ElasticDeformation"
                                                      , "AffineTransformation"
                                                      ]
                             , "Postprocessing": [ {"Activation": "Sigmoid"}
                                                 , {"Threshold":  0.9}
                                                 ]
                             , "Model type": "U-Net big"
                             , "number input channel": 2 
                             , "channel types input": ["clahe", "nl_means"]
                             , "number output channel": 1
                             , "channel types output": ["identity"] 
                             , "optimizer": "Adam"
                             , "loss function": "Dice loss"
                             , "metrics": ["Dice Metric"]
                             }
    #entries in dict_model_and_training can be changed!!
    #maybe other input channels because images have other properties (e.g blurring)
else:
    dict_model_and_training = { "ROI training": 512
                              , "ROI validation": 512
                              , "Augementation probability": 0.5
                              , "Preprocessing steps": ["ScaleIntensity"]
                              , "Augmentation steps": [ "SpatialCrop"
                                                      #, "GaussianNoise"
                                                      , "Rotate"
                                                      , "Flip"
                                                      , "Zoom"
                                                      #, "ElasticDeformation"
                                                      #, "AffineTransformation"
                                                      ]
                              , "Postprocessing": [ {"Activation": "Sigmoid"}
                                                  , {"Threshold":  0.9}
                                                  ]
                              , "Model type": "UNetTransformer"
                              , "number input channel": 2 
                              , "channel types input": ["clahe", "nl_means"]
                              , "number output channel": 1
                              , "channel types output": ["identity"] 
                              , "optimizer": "AdamW"
                              , "loss function": "Dice CE loss"
                              , "metrics": ["Dice Metric"]
                              }
    model_name = dict_model_and_training["Model type"]
    input_channels = dict_model_and_training["number input channel"]
    output_channels = dict_model_and_training["number output channel"]
    experiment_parameter["model type"] = model_name
    image_size = dict_model_and_training["ROI training"]
    model = get_model( model_name
                     , input_channels
                     , output_channels
                     , device
                     , image_size
                     )
    swa_model = torch.optim.swa_utils.AveragedModel(model)
#specify on which data you want to train
list_training_on_data = []
list_training_on_data =  [ { "path images": [ '/home/webern/idsair_public/data/interpolated_images/train/img'
                                           ]
                          , "path masks": [ '/home/webern/idsair_public/data/interpolated_images/train/mask'
                                          ]
                          , "path val images":  [ '/home/webern/idsair_public/data/interpolated_images/val/img'
                                                ]
                          , "path val masks":  [ '/home/webern/idsair_public/data/interpolated_images/val/mask'
                                               ]
                          , "validation intervall": 10
                          }
                         ]
"""
list_training_on_data =  [ { "path images": ['/home/webern/idsair_public/data/mean_images_ina/train/img'
                                            , '/home/webern/idsair_public/data/mean_images_julian/train/img'
                                            , '/home/webern/idsair_public/data/frame_images_ina/train/img'
                                            ]
                          , "path masks":  ['/home/webern/idsair_public/data/mean_images_ina/train/mask'
                                           , '/home/webern/idsair_public/data/mean_images_julian/train/mask'
                                           , '/home/webern/idsair_public/data/frame_images_ina/train/mask'
                                           ]
                          , "path val images":  ['/home/webern/idsair_public/data/mean_images_ina/val/img'
                                                , '/home/webern/idsair_public/data/mean_images_julian/val/img'
                                                , '/home/webern/idsair_public/data/frame_images_ina/val/img'
                                                ]
                          , "path val masks":  ['/home/webern/idsair_public/data/mean_images_ina/val/mask'
                                               , '/home/webern/idsair_public/data/mean_images_julian/val/mask'
                                               , '/home/webern/idsair_public/data/frame_images_ina/val/mask'
                                               ]
                          , "validation intervall": 10
                          }
                         ]
"""

# create files. Target directories should not exist.
working_dir = path_save_folder
#create folders with summary and trained weights
Path(working_dir).mkdir(parents = True, exist_ok = False)
with open(working_dir + "/Experiment_parameter.json", 'a') as File:
    dict_model_and_training["data_training"] = list_training_on_data
    json.dump(dict_model_and_training, File, indent = 2)

Path(working_dir + "/trained_weights").mkdir(parents = True, exist_ok = False)
Path(working_dir + "/trained_weights_swa").mkdir(parents = True, exist_ok = False)
Path(working_dir + "/predictions").mkdir(parents = True, exist_ok = False)

list_preprocessing_steps = preprocessing(dict_model_and_training["Preprocessing steps"])  
list_augmentations_steps = augmentation( dict_model_and_training["Augmentation steps"]
                                       , dict_model_and_training["ROI training"]
                                       , dict_model_and_training["Augementation probability"]
                                       )
list_to_tensor = convert_to_tensor()
trans_train = Compose(list_preprocessing_steps + list_augmentations_steps + list_to_tensor)
trans_val = Compose(list_preprocessing_steps + list_to_tensor)
postprocessing_steps = postprocessing(dict_model_and_training["Postprocessing"])

channelManipulationInput = dict_model_and_training["channel types input"]
channelManipulationOutput = dict_model_and_training["channel types output"]
#model.train()
#First step: pretraining on public available dataset from dsb2018. Goal: learn general image structures
#Second step: Train on interpolated images of IDSAIR datasets. Goal: With this method we can generate more data with more
#complicated structures
#Third step: Make a short training on IDSAIR datas.
loss_type = dict_model_and_training["loss function"]
experiment_parameter["loss type"] = loss_type
if loss_type == "Dice loss":
    loss_function = DiceLoss( sigmoid = True
                            , squared_pred = True
                            , jaccard = True
                            , reduction = "mean")
if loss_type == "Focal loss":
    loss_function = FocalLoss( to_onehot_y = True)
if loss_type == "Tversky loss":
    loss_function = TverskyLoss( sigmoid = True
                               , reduction = "mean"
                               )
if loss_type == "Dice focal loss":
    loss_function = DiceLoss( sigmoid = True
                            , squared_pred = True
                            , jaccard = True
                            , reduction = "mean")
if loss_type == "Dice CE loss":
    #loss_function = DiceCELoss( sigmoid = True
    #                        , squared_pred = True
    #                        , jaccard = True
    #                        , reduction = "mean")
    loss_function = DiceCELoss( sigmoid = True
                              )
if "Dice Metric" in dict_model_and_training["metrics"]:
    metric = DiceMetric( include_background = True
                       , reduction = "mean"
                       )
optimizer_name = dict_model_and_training["optimizer"]
experiment_parameter["optimizer"] = optimizer_name
for data in list_training_on_data:
    if optimizer_name == "Adam":
        opt = torch.optim.Adam(model.parameters(), learning_rate)
    if optimizer_name == "AdamW":
        opt = torch.optim.AdamW(model.parameters(), lr = learning_rate, weight_decay = 1e-5)
    train_recordings, _ = DataReader( data["path images"]
                                    , data["path masks"]
                                    , 0
                                    )
    _ , val_recordings = DataReader( data["path val images"]
                                    , data["path val masks"]
                                    , 1
                                    )
    
    data_train = [ { "img": channelProcessingInput(train_recordings[i].image, channelManipulationInput)
                   , "seg": channelProcessingOutput(train_recordings[i].label, channelManipulationOutput)
                   } for i in range(len(train_recordings))
                 ]
    data_val = [ { "img": channelProcessingInput(val_recordings[i].image, channelManipulationInput)
                 , "seg": channelProcessingOutput(val_recordings[i].label, channelManipulationOutput)
                 } for i in range(len(val_recordings))
              ]
    model, swa_model, loss_function, opt = train( model
                                                , swa_model
                                                , data_train
                                                , trans_train
                                                , data_val
                                                , trans_val
                                                , epochs
                                                , batch_size
                                                , data["validation intervall"]
                                                , loss_function
                                                , opt
                                                , metric
                                                , postprocessing_steps
                                                , device
                                                )
    del data_train
    del data_val
torch.save(model.state_dict(), working_dir + "/trained_weights/" + "trained_weights.pth")
if swa_model != None:
    torch.save(swa_model.state_dict(), working_dir + "/trained_weights_swa/" + "trained_weights.pth")
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

