import os
import torch
import time

from torchelper.models.model_builder import ModelBuilder
 
from .callback import Callback
from torchelper.models.base_model import BaseModel
from torchelper.utils.dist_util import master_only, get_bare_model
from torchelper.utils import logger

class CkptCallback(Callback):
    def __init__(self, ckpt_dir, name, restore_epoch=-1,
                 max_ckpts=10,
                 save_per_secs=2*60*60,
                 strict=False,
                 save_before_train=True,
                 best_metric_name=None):
        super().__init__()
        self.name = name
        self.best_metric_name = best_metric_name
        self.strict = strict
        self.ckpt_dir = ckpt_dir
        self.restore_epoch = restore_epoch
        self.epochs = []
        self.last_save_time = -1
        self.max_ckpts=max_ckpts
        self.save_per_secs = save_per_secs
        self.save_before_train = save_before_train
        self.best_metric = self.__find_cur_best_model()
    
    def __find_cur_best_model(self):
        names = os.listdir(self.ckpt_dir)
        cur_best = -1
        for name in names:
            if name.startswith('best_'):
                fbest = name[0:-4].split('_')[-1]
                best = float(fbest)
                if best >cur_best:
                    cur_best = best
        return cur_best

    def load_weights(self, model, epoch):
        # 1. load weights
        save_filename = "%s_weights_%s.pth" % (epoch, self.name)
        save_path = os.path.join(self.ckpt_dir, save_filename)
        if os.path.exists(save_path):
            weights = torch.load(save_path, map_location=lambda storage, loc: storage)
            weights = get_bare_model(model).remap_weights_name(weights)
            get_bare_model(model).load_state_dict(weights, strict=self.strict)
            logger.log("success load model:"+ save_path)
        else:
            logger.log("%s not exists yet!" % save_path)
            return False
        
        # 2. load optimizer
        optimizer = get_bare_model(model).get_optimizer()
        if optimizer is not None:
            save_filename = "%s_optimizer_%s.pth" % (epoch, self.name)
            save_path = os.path.join(self.ckpt_dir, save_filename)
            if not os.path.isfile(save_path):
                logger.log("%s not exists yet!" % save_path)
                return False
            else:
                weights = torch.load(save_path, map_location=lambda storage, loc: storage)
                try:
                    optimizer.load_state_dict(weights)
                except:
                    logger.log('Failed to load optimizer parameters')
                    return False
                logger.log("success load optimizer:", save_path)
        return True
    
    def __is_best(self, metric_dict:dict):
        if self.best_metric_name is None:
            return False
 
        if metric_dict is None:
            return False

        metric = metric_dict.get(self.best_metric_name, -1)
        if metric > self.best_metric:
            self.best_metric = metric
            return True
        return False

    @master_only
    def __save_if_best(self, model:BaseModel, epoch:int, metric_dict:dict):
        if not self.__is_best(metric_dict):
            return
        if self.best_metric is None:
            return
        opt_name = "best_%s_opt_%s_%.5f.pth" % (epoch, self.name, self.best_metric)
        weight_name = "best_%s_w_%s_%.5f.pth" % (epoch, self.name, self.best_metric)
        opt_path = os.path.join(self.ckpt_dir, opt_name)
        weight_path = os.path.join(self.ckpt_dir, weight_name)
        self.__save_model(model, opt_path, weight_path)
        names = os.listdir(self.ckpt_dir)
        valid_pre = "best_%s_"%(epoch)
        for name in names:
            if name.startswith('best_') and not name.startswith(valid_pre):
                os.remove(os.path.join(self.ckpt_dir, name))

    def __save_model(self, model:BaseModel, opt_path:str, weight_path:str):
        #1. save optimizer
        optimizer = model.get_optimizer()
        if optimizer is not None:
            torch.save(optimizer.state_dict(), opt_path)
            logger.log('save:', opt_path)

        #2. save weights
        torch.save(get_bare_model(model).state_dict(), weight_path)
        logger.log('save:', weight_path)

    @master_only
    def save_model(self, model:BaseModel, epoch):
        save_opt_name = "%s_optimizer_%s.pth" % (epoch, self.name)
        save_opt_path = os.path.join(self.ckpt_dir, save_opt_name)
        save_weight_filename = "%s_weights_%s.pth" % (epoch, self.name)
        save_weight_path = os.path.join(self.ckpt_dir, save_weight_filename)
        self.__save_model(model, save_opt_path, save_weight_path)

        #1. save optimizer
        # optimizer = model.get_optimizer()
        # if optimizer is not None:
        #     save_opt_name = "%s_optimizer_%s.pth" % (epoch, self.name)
        #     save_opt_path = os.path.join(self.ckpt_dir, save_opt_name)
            
        #     # torch.save(optimizer.state_dict(), save_opt_path)
        #     # print('save:', save_opt_path)

        # #2. save weights
        # save_weight_filename = "%s_weights_%s.pth" % (epoch, self.name)
        # save_weight_path = os.path.join(self.ckpt_dir, save_weight_filename)
        # torch.save(get_bare_model(model).state_dict(), save_weight_path)
        # print('save:', save_weight_path)

        #3. clear old
        if self.max_ckpts<=0: #不清除
            return
        # 每间隔max_time时间保存一次
        if time.time() - self.last_save_time > self.save_per_secs:
            self.last_save_time = time.time()
        else:
            if epoch not in self.epochs:
                self.epochs.append(epoch)
            while len(self.epochs) > self.max_ckpts:
                opt_name = '%s_optimizer_%s.pth'%(self.epochs[0], self.name)
                weight_name = '%s_weights_%s.pth'%(self.epochs[0], self.name)
                opt_path = os.path.join(self.ckpt_dir, opt_name)
                weight_path = os.path.join(self.ckpt_dir, weight_name)
                print(opt_path)
                if os.path.exists(opt_path):
                    os.remove(opt_path)
                if os.path.exists(weight_path):
                    os.remove(weight_path)
                del self.epochs[0]


    def on_begin_train(self, model:BaseModel, epoch:int):
        self.load_weights(model, self.restore_epoch)
        
        if self.save_before_train and epoch==0:
            self.save_model(model, -1)
        
    def on_end_val(self, model:BaseModel, epoch:int, metric_dict:dict):
        self.__save_if_best(model, epoch, metric_dict)

    def on_end_train(self, model:BaseModel):
        pass

    def on_begin_epoch(self, model:BaseModel, epoch:int):
        pass

    def on_end_epoch(self, model:BaseModel, epoch:int):
        self.save_model(model, epoch)

    def on_begin_step(self, model:BaseModel, epoch:int, step:int):
        pass

    def on_end_step(self, model:BaseModel, epoch:int, step:int):
        pass