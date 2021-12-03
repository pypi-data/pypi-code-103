# Copyright 2021 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Exception checkpoint related classes and functions."""

import os
import time
import signal

import moxing as mox
from mindspore.train.callback import Callback, CheckpointConfig
from mindspore.train.serialization import save_checkpoint, _save_graph
from mindspore.parallel._ps_context import _is_role_pserver, _get_ps_mode_rank
from mindspore.train._utils import _make_directory
from mindspore.train.callback import ModelCheckpoint

_cur_dir = os.getcwd()

def _check_bpckpt_file_name_if_same_exist(directory, prefix):
    """Check if there is a file with the same name."""
    files = os.listdir(directory)
    suffix_num = 0
    pre_len = len(prefix)
    for filename in files:
        if filename[-16:] != "_breakpoint.ckpt":
            continue
        # find same prefix file
        if filename.find(prefix) == 0 and not filename[pre_len].isalpha():
            # add the max suffix + 1
            index = filename[pre_len:].find("-")
            if index == 0:
                suffix_num = max(suffix_num, 1)
            elif index != -1:
                num = filename[pre_len + 1:pre_len + index]
                if num.isdigit():
                    suffix_num = max(suffix_num, int(num) + 1)
    if suffix_num != 0:
        prefix = prefix + "_" + str(suffix_num)
    return prefix

class ExceptionCheckpoint(ModelCheckpoint):
    def __init__(self, prefix='CKP', directory=None, mox_dir=None, config=None):
        super(ExceptionCheckpoint, self).__init__(prefix, directory, config)
        signal.signal(signal.SIGTERM, self.save)
        signal.signal(signal.SIGINT, self.save)
        self.epoch_time = 0
        self.mox_dir = mox_dir

    def __exit__(self, *err):
        pass

    def begin(self, run_context):
        """
        Called once before the network executing.

        Args:
            run_context (RunContext): Include some information of the model.
        """
        self.cb_params = run_context.original_args()

    def epoch_begin(self, run_context):
        if self.epoch_time >= 10:
            print(f"epoch {self.epoch_time} fault")
            self.save(0, 0)
        self.epoch_time = self.epoch_time + 1

    def _save_ckpt(self, cb_params, force_to_save=False):
        """Save checkpoint files."""
        if cb_params.cur_step_num == self._last_triggered_step:
            return

        # if param is cache enable, flush data from cache to host before save_ckpt
        if self._need_flush_from_cache:
            self._flush_from_cache(cb_params)

        save_ckpt = self._check_save_ckpt(cb_params, force_to_save)
        step_num_in_epoch = int((cb_params.cur_step_num - 1) % cb_params.batch_num + 1)

        if save_ckpt:
            cur_ckpoint_file = self._prefix + "-" + str(cb_params.cur_epoch_num) + "_" \
                + str(step_num_in_epoch) + ".ckpt"
            # update checkpoint file list.
            self._manager.update_ckpoint_filelist(self._directory, self._prefix)
            # keep checkpoint files number equal max number.
            if self._config.keep_checkpoint_max and 0 < self._config.keep_checkpoint_max <= self._manager.ckpoint_num:
                self._manager.remove_oldest_ckpoint_file()
            elif self._config.keep_checkpoint_per_n_minutes and self._config.keep_checkpoint_per_n_minutes > 0:
                self._cur_time_for_keep = time.time()
                if (self._cur_time_for_keep - self._last_time_for_keep) \
                        < self._config.keep_checkpoint_per_n_minutes * 60:
                    self._manager.keep_one_ckpoint_per_minutes(self._config.keep_checkpoint_per_n_minutes,
                                                               self._cur_time_for_keep)

            # generate the new checkpoint file and rename it.
            global _save_dir
            _save_dir = self._directory
            cur_file = os.path.join(self._directory, cur_ckpoint_file)
            self._last_time_for_keep = time.time()
            self._last_triggered_step = cb_params.cur_step_num

            if context.get_context("enable_ge"):
                cb_params.train_network.exec_checkpoint_graph()
            if "epoch_num" in self._append_dict:
                self._append_dict["epoch_num"] = self._append_epoch_num + cb_params.cur_epoch_num
            if "step_num" in self._append_dict:
                self._append_dict["step_num"] = self._append_step_num + cb_params.cur_step_num
            network = self._config.saved_network if self._config.saved_network is not None else cb_params.train_network
            save_checkpoint(network, cur_file, self._config.integrated_save, self._config.async_save,
                            self._append_dict, self._config.enc_key, self._config.enc_mode)

            mox.file.copy(cur_file, self.mox_dir)
            self._latest_ckpt_file_name = cur_file

    def save(self, signum, frame):
        """
        Save current checkpoint when an error is occur.
        """
        print(f"process sig {signum} and frame content {frame}")
        if self.cb_params is None:
            return

        prefix = _check_bpckpt_file_name_if_same_exist(self._directory,
                                                       self._prefix)
        step_num_in_epoch = int(
            (self.cb_params.cur_step_num - 1) % self.cb_params.batch_num + 1)

        cur_ckpt_file = f"Exception-{self.cb_params.cur_epoch_num}_{step_num_in_epoch}_breakpoint.ckpt"
        cur_file = os.path.join(self._directory, cur_ckpt_file)

        if "epoch_num" in self._append_dict:
            self._append_dict[
                "epoch_num"] = self._append_epoch_num + self.cb_params.cur_epoch_num
        if "step_num" in self._append_dict:
            self._append_dict[
                "step_num"] = self._append_step_num + self.cb_params.cur_step_num
        network = self._config.saved_network if self._config.saved_network is not None else self.cb_params.train_network

        save_checkpoint(network, cur_file, self._config.integrated_save,
                        self._config.async_save,
                        self._append_dict, self._config.enc_key,
                        self._config.enc_mode)
        mox.file.copy(cur_file, self.mox_dir)
        raise RuntimeError("Term exception happened.")
