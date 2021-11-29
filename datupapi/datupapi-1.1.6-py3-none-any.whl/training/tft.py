import os
import warnings
import pandas as pd
import featurewiz as FW
import numpy as np
import copy
from pathlib import Path
import warnings
import pytorch_lightning as pl
from pytorch_lightning.callbacks import EarlyStopping, LearningRateMonitor
from pytorch_lightning.loggers import TensorBoardLogger
import torch
import gc
from tensorflow.keras import backend as K
from dateutil.relativedelta import relativedelta
from datetime import datetime
import time
from datupapi.extract.io import IO
from datupapi.configure.config import Config
from datupapi.predict.forecast import Forecast
from pytorch_forecasting import Baseline, TemporalFusionTransformer, TimeSeriesDataSet, DeepAR, NBeats
from pytorch_forecasting.data import GroupNormalizer, EncoderNormalizer, TorchNormalizer
from pytorch_forecasting.metrics import SMAPE, PoissonLoss, QuantileLoss, RMSE, MASE, MAPE, MAE, NormalDistributionLoss
from pytorch_forecasting.models.temporal_fusion_transformer.tuning import optimize_hyperparameters

class Tft(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path

    def transform_to_matrix(self, df, value=None, method=None):
        """
        Returns a dataframe in matrix form in order to be trained by the attention model

        :param df: Dataframe with columns: timestamp, item_id and demand
        :return df_out: Output dataframe with each item as a column
        >>> df =
                Date        item_id  Demand
                2021-16-05     sku1      23
                2021-16-05     sku2     543
                2021-16-05     sku3     123
        >>> df = transform_to_matrix(df)
        >>> df =
                      Date           sku1    sku2     sku3 ......... skuN
                idx1  2021-16-05      23      543      123 ......... 234
        """
        df_out = df.sort_values(by='timestamp')
        df_out = df_out.reset_index()
        df_out = df_out.iloc[:, 1:]
        df_out = df_out.pivot(index='timestamp', columns='item_id', values='demand').reset_index()
        df_out = df_out.fillna(value=value, method=method)
        df_out = df_out.rename(columns={'timestamp': 'Date'})
        df_out=df_out.set_index("Date")
        df_out =df_out.reindex(sorted(df_out.columns), axis=1)
        df_out=df_out.reset_index()
        for_loc = []
        return df_out, for_loc

    def date_index_generator(self, date_data, data_range):
        for index, date in enumerate(data_range):
            if date_data==date:
                return index

    def clean_negatives(self, df):
        """
        Replace negative values with zeros.

        :param noneg (df): Dataframe with the negative values to be replaces.
        :param n_backtests (int): Number of backtests. 5 by default.

        :return noneg (df): Dataframe without negative values.
        """
        inter = ["p95", "p5", "p60", "p40", "p80", "p20", "p50"]
        for i in range(1, self.backtests + 1):
            df[i]['target_value'] = df[i]['target_value'].map(lambda x: 0 if x < 0 else x)

        for i in inter:
            for j in range(self.backtests + 1):
                df[j][i] = df[j][i].map(lambda x: 0 if x < 0 else x)

        return df
    
    def add_dates(self, Qprep, data1, predict, suffix):
        data_range=pd.date_range(start=Qprep.timestamp.min(), end=Qprep.timestamp.max().date()+relativedelta(months=self.forecast_horizon), freq=self.dataset_frequency+suffix) if self.dataset_frequency=="M" else pd.date_range(start=Qprep.timestamp.min(), end=Qprep.timestamp.max().date()+relativedelta(weeks=self.forecast_horizon), freq=self.dataset_frequency+suffix)
        #data_range=pd.date_range(start=Qprep.timestamp.min(), end=datetime.strptime(Qprep.timestamp.max(), '%Y-%m-%d').date()+relativedelta(months=trng.n_steps_out), freq=frequency+suffix) if frequency=="M" else pd.date_range(start=Qprep.timestamp.min(), end=datetime.strptime(Qprep.timestamp.max(), '%Y-%m-%d').date()+relativedelta(weeks=trng.n_steps_out), freq=frequency+suffix)
        predict[0]["date"]=predict[0].apply(lambda row: data_range[row["time_idx"]], axis=1)
        column_names=["item_id","location", "date","p5","p20","p40","p50","p60","p80","p95"] if self.use_location else ["item_id","date","p5","p20","p40","p50","p60","p80","p95"]
        predict[0] = predict[0].reindex(columns=column_names)
        data1.item_id=data1.item_id.astype("string")
        for i in range(1, self.backtests+1):
            if self.use_location:
                predict[i].location=predict[i].location.astype("string")
                data1.location=data1.location.astype("string")
            predict[i].item_id=predict[i].item_id.astype("string")
            predict[i]["timestamp"]=predict[i].apply(lambda row: data_range[row["time_idx"]], axis=1)
            predict[i]=predict[i].assign(backtestwindow_start_time=data_range[predict[i].time_idx.min()])
            predict[i]=predict[i].assign(backtestwindow_end_time=data_range[predict[i].time_idx.max()])
            predict[i]=predict[i].merge(data1[["time_idx", "item_id","location", "demand"]], on=["time_idx", "item_id", "location"]) if self.use_location else predict[i].merge(data1[["time_idx", "item_id","demand"]], on=["time_idx", "item_id"])
            predict[i]=predict[i].rename(columns={"demand":"target_value"})
            column_names=["item_id","location", "timestamp","target_value","backtestwindow_start_time","backtestwindow_end_time","p5","p20", "p40","p50","p60","p80","p95"] if self.use_location else ["item_id","timestamp","target_value","backtestwindow_start_time","backtestwindow_end_time","p5","p20", "p40","p50","p60","p80","p95"]
            predict[i] = predict[i].reindex(columns=column_names)
        return predict
    
    def create_training_dataset(self, data1, training_cutoff, group_ids, max_encoder_length, max_prediction_length, unknown, known):
        target_normalizer=EncoderNormalizer() if self.normalization else GroupNormalizer(groups=["item_id"], transformation="softplus")
    
        training = TimeSeriesDataSet(
            data1[data1.time_idx <= training_cutoff],
            time_idx="time_idx",
            target="demand",
            group_ids=group_ids,
            min_encoder_length=max_encoder_length ,  # keep encoder length long (as it is in the validation set)
            max_encoder_length=max_encoder_length,
            min_prediction_length=max_prediction_length,
            max_prediction_length=max_prediction_length,
            time_varying_unknown_reals=unknown,
            time_varying_known_reals=known,
            target_normalizer=target_normalizer,
            add_relative_time_idx=True,
            add_target_scales=True,
            add_encoder_length=True,

        )
        return training

    def create_trainer(self, callbacks, logger):
        trainer = pl.Trainer(
            max_epochs=self.epochs_tft,
            gpus=0,
            weights_summary="top",
            gradient_clip_val=self.gradient_clip_val,
            limit_train_batches=100,  # coment in for training, running valiation every 30 batches
            # fast_dev_run=True,  # comment in to check that networkor dataset has no serious bugs
            callbacks=callbacks,
            logger=logger
            )
        return trainer  

    def create_tft(self, training):
        tft = TemporalFusionTransformer.from_dataset(
            training,
            learning_rate=self.lr_tft,
            lstm_layers=self.lstm_layers,
            hidden_size=self.hidden_size,
            attention_head_size=self.attention_head_size,
            dropout=self.dropout_train,
            hidden_continuous_size=self.hidden_continuous_size,
            output_size=7,  # 7 quantiles by default
            loss=QuantileLoss(quantiles=[0.05, 0.2, 0.4, 0.5,0.6, 0.8, 0.95 ]),
            log_interval=10,  # uncomment for learning rate finder and otherwise, e.g. to 10 for logging every 10 batches
            reduce_on_plateau_patience=4,
        )
        return tft


    def fill_dates(self, Qprep, value=0, method=None):
        if self.use_location:
            Qprep["item_id"]=Qprep.apply(lambda row: (str(row["item_id"])+"-"+str(row["location"])),axis=1)
            Qprep=Qprep[["timestamp","item_id","demand"]]

        data_date,_=self.transform_to_matrix(Qprep, value=value, method=method)
        Qprep= data_date.set_index('Date')\
                 .stack()\
                 .reset_index(drop=False)\
                 .rename(columns={'level_1': 'item_id', 0: 'demand'})\
                 .sort_values(by='Date',ascending=True)
        Qprep.columns=["timestamp","item_id","demand"]
        if self.use_location:
            Qprep["location"]=Qprep.apply(lambda row: row["item_id"].split("-")[1], axis=1)
            Qprep["item_id"]=Qprep.apply(lambda row: row["item_id"].split("-")[0], axis=1)

        return Qprep
