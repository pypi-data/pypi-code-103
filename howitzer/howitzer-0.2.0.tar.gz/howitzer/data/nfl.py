from __future__ import print_function, division
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import torch
import os
__dirname = os.path.dirname(__file__)


def getAllGames():
    return pd.read_csv(os.path.join(__dirname,'files/nfl-all-games.csv'), index_col="index")

def getAllGameStats():
    return pd.read_csv(os.path.join(__dirname,'files/nfl-all-team-stats.csv'), index_col="index")

def getRolling3GameAverage():
    return pd.read_csv(os.path.join(__dirname,'files/machiene-readable-3-week-look-back.csv'))

class NflGameDataset(Dataset):
    """NFL Game Result dataset"""
    
    def __init__(self, csv_file="", transforms=None):
        """
        Args:
            csv_file (string): Path to the csv file containing the results data
        """
        
        self.game_frame = pd.read_csv(csv_file)
        self.transforms = transforms
        
    def __len__(self):
         return len(self.game_frame)
        
    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
                
        stats = self.game_frame.iloc[idx, :-1]
        result = self.game_frame.iloc[idx, -1:]
            
        sample = {"result":result, "stats":stats}
            
        if self.transforms:
            sample = self.transforms(sample)
            
        return sample