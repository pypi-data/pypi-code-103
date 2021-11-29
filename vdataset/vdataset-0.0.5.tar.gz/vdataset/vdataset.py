from torch.utils.data import Dataset
import pandas as pd
from PIL import Image
from pathlib import Path
from .labelmap import LabelMap


class VDataset(Dataset):
    """
    VDataset

    This class is a subclass of the PyTorch Dataset class. It is used to load the videos from the dataset.

    Parameters
    ----------
    csv_file : str
        The path to the csv file containing the dataset.
    root_dir : str
        The path to the root directory of the dataset.
    file_format : str, optional
        The format of the video files. The default is "jpg".
    id_col_name : str, optional
        The name of the column containing the video ids. The default is "video_id".
    label_col_name : str, optional
        The name of the column containing the labels. The default is "label".
    frames_limit_mode : str, optional
        The mode to limit the number of frames. Can be "manual", "csv" or None. The default is None.
    frames_limit : int, optional
        The number of frames to limit the dataset to. The default is 1.
    frames_limit_col_name : str, optional
        The name of the column containing the number of frames. The default is "frames".
    video_transforms : object, optional
        The transformations to apply to the loaded videos. The default is None. (Refere https://github.com/hassony2/torch_videovision)
    label_map : LabelMap, optional
        The label map to use. The default is None. (refere https://github.com/nzx9/vdataset)

    Returns
    -------
    VDataset
        The VDataset object.
    """

    def __init__(self, csv_file: str, root_dir: str, file_format: str = "jpg", id_col_name: str = "video_id", label_col_name: str = "label", frames_limit_mode: str = None, frames_limit: int = 1, frames_limit_col_name: str = "frames", video_transforms=None, label_map: LabelMap = None):
        self.dataframe = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.file_format = '*{}'.format(
            file_format) if file_format[0] == "." else '*.{}'.format(file_format)
        self.id_col_name = id_col_name
        self.label_col_name = label_col_name
        self.frames_limit_mode = frames_limit_mode
        self.frames_limit = frames_limit
        self.frames_limit_col_name = frames_limit_col_name
        self.transform = video_transforms
        self.label_map = label_map

    def __getitem__(self, index):
        row = self.dataframe.iloc[index]
        label_name = row[self.label_col_name]

        if self.label_map != None:
            label = self.label_map.to_id(label_name)
            if label == None:
                raise ValueError("label can't be None")
        else:
            label = label_name
        video_id = row[self.id_col_name]

        if self.frames_limit_mode == "csv":
            self.frames_limit = row[self.frames_limit_col_name]

        frames_list = list(
            Path('{}/{}'.format(self.root_dir, video_id)).glob(self.file_format))

        if len(frames_list) == 0:
            raise FileNotFoundError('Error: No frames found.')
        elif (self.frames_limit_mode == "manual" or self.frames_limit_mode == "csv") and (len(frames_list) > self.frames_limit):
            frames_list = frames_list[0: self.frames_limit]

        frames = [Image.open(f).convert('RGB') for f in frames_list]

        if self.transform:
            frames = self.transform(frames)
        return frames, label

    def __len__(self) -> int:
        return len(self.dataframe)
