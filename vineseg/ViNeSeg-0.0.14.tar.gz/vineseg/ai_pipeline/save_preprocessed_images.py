from DataLoader import DataReader
from add_channels import channelProcessingInput, channelProcessingOutput
from util import save_as_image
"""
The variabels path_channel_one, path_channel_two and path_image_folder
must be set to your local machine.
path_channel_one: Specify the location, where to store the clahe preprocessed images.
path_channel_two: Specify the location, where to store the nl means preprocessed images.
path_image_folder: A list of folders from where we want to load the images for preprocessing.
"""
path_channel_one = '/home/webern/idsair_public/channel_one/'
path_channel_two = '/home/webern/idsair_public/channel_two/'
path_image_folder = ['/home/webern/idsair_public/data/mean_images_ina/test/img'
                    , '/home/webern/idsair_public/data/mean_images_julian/test/img'
                    , '/home/webern/idsair_public/data/frame_images_ina/test/img'
                    ]

_, val_recordings = DataReader( path_image_folder
                              , []
                              , 1
                              )

channelManipulationInput = ["clahe", "nl_means"]
first_channel = [channelProcessingInput(val_recordings[i].image, channelManipulationInput)[0] for i in range(len(val_recordings))]
second_channel = [channelProcessingInput(val_recordings[i].image, channelManipulationInput)[1] for i in range(len(val_recordings))]
list_data_names = [val_recordings[i].name for i in range(len(val_recordings))]
dict_channel_one = {}
dict_channel_two = {}
for index, name in enumerate(list_data_names):
    dict_channel_one[name] = 255*first_channel[index]
    dict_channel_two[name] = 255*second_channel[index]
save_as_image(dict_channel_one, path_channel_one)
save_as_image(dict_channel_two, path_channel_two)
