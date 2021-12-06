# MIT License

# Copyright (c) 2021 Hao Yang (yanghao.alexis@foxmail.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import time
import os
from typing import List
from collections import defaultdict

import torch
from torch import distributed as dist
import torchvision

from ..context import Context


def _tagged(s: str, tag) -> str:
    if tag is None:
        return s
    return f'{tag}.{s}'


class Logger:
    def setup(self, outputs_dir):
        pass

    def log_info(self, msg):
        pass

    def log_batched_images(self, outputs, global_step=None, epoch=None, tag=None):
        pass

    def log_numbers(self, numbers: dict, global_step=None, epoch=None, tag=None):
        pass


class Loggers(Logger):
    def __init__(self, loggers: List[Logger]) -> None:
        self.loggers = loggers

    def setup(self, outputs_dir):
        for logger in self.loggers:
            logger.setup(outputs_dir)

    def log_info(self, msg):
        for logger in self.loggers:
            logger.log_info(msg)

    def log_batched_images(self, outputs, global_step=None, epoch=None, tag=None):
        for logger in self.loggers:
            logger.log_batched_images(outputs, global_step, epoch, tag)

    def log_numbers(self, numbers: dict, global_step=None, epoch=None, tag=None):
        for logger in self.loggers:
            logger.log_numbers(numbers, global_step, epoch, tag)


class Printer(Logger):
    def __init__(self):
        self.on_main_thread = not dist.is_initialized() or torch.cuda.current_device() == 0

    def log_info(self, msg):
        formated_msg = f'{time.asctime(time.localtime())} - {msg}'
        if self.on_main_thread:
            print(formated_msg, flush=True)


class StandardLogger(Logger):
    def __init__(self, _ctx: Context):
        self.context = _ctx

    def setup(self, outputs_dir):
        self.outputs_dir = outputs_dir

        if not dist.is_initialized():
            suffix = ''
        else:
            suffix = f'_{dist.get_rank()}'
        self.name = self.context.exp_name + suffix

        self.on_main_thread = not dist.is_initialized() or torch.cuda.current_device() == 0

        # create file handler
        os.makedirs(self.outputs_dir, exist_ok=True)

        self.files = [
            open(os.path.join(self.outputs_dir,
                              f'log{suffix}.txt'), 'a')]

        if self.on_main_thread:
            os.makedirs(os.path.join(
                self.outputs_dir, 'css'), exist_ok=True)
            with open(os.path.join(self.outputs_dir, 'css', 'style.css'), 'w') as f:
                f.write(r'''
                    .styled-table {
                        border-collapse: collapse;
                        margin: 25px 0;
                        font-size: 0.9em;
                        font-family: sans-serif;
                        min-width: 400px;
                        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                    }
                    .styled-table thead tr {
                        background-color: #009879;
                        color: #ffffff;
                        text-align: left;
                    }
                    .styled-table th,
                    .styled-table td {
                        padding: 12px 15px;
                    }
                    .styled-table tbody tr {
                        border-bottom: 1px solid #dddddd;
                    }

                    .styled-table tbody tr:nth-of-type(even) {
                        background-color: #f3f3f3;
                    }

                    .styled-table tbody tr:last-of-type {
                        border-bottom: 2px solid #009879;
                    }

                    .styled-table tbody tr.active-row {
                        font-weight: bold;
                        color: #009879;
                    }
                ''')

    def __del__(self):
        for f in self.files:
            f.close()
        self.files.clear()

    def _print(self, msg: str):
        formated_msg = f'{time.asctime(time.localtime())} - {self.name} - {msg}'
        if self.on_main_thread:
            print(formated_msg, flush=True)
        for f in self.files:
            f.write(formated_msg + '\n')
            f.flush()

    def log_info(self, msg):
        self._print(msg)

    def log_batched_images(self, outputs, global_step=None, epoch=None, tag=None):
        if not dist.is_initialized() or torch.cuda.current_device() == 0:
            html = (f'<html><head><title>global_step={global_step}, epoch={epoch}</title>'
                    f'</head><body><table class="styled-table">')
            # write titles
            names = list(outputs.keys())
            html += '<thead><tr>'
            for name in names:
                html += f'<th>{name}</th>'
            html += '</tr></thead><tbody>'
            html += '<tr>'
            for name in names:
                image_batch = outputs[name]
                image_file_name = _tagged(f'{name}.png', tag)
                image_file_path = os.path.join(
                    self.outputs_dir, image_file_name)
                torchvision.utils.save_image(
                    image_batch, image_file_path, normalize=False, nrow=1)
                html += f'<td><img src="{image_file_name}" width="250"/></td>'
            html += '</tr>'
            html += '</tbody></table></body></html>'

            with open(os.path.join(self.outputs_dir, _tagged(f'images.html', tag)), 'w') as f:
                f.write(html)

    def log_numbers(self, numbers: dict, global_step=None, epoch=None, tag=None):
        line = ''
        for name, val in numbers.items():
            line += f'{_tagged(name, tag)}={val} '
        self._print(
            f'[global_step={global_step}, epoch={epoch}] {line}')


class TSVDataLogger(Logger):
    def __init__(self, _ctx=None):
        self.context = _ctx

    def setup(self, outputs_dir):
        self.outputs_dir = outputs_dir

        # create file handler
        os.makedirs(self.outputs_dir, exist_ok=True)

        if dist.is_initialized():
            self.rank = dist.get_rank()
            self.suffix = f'_{self.rank}'
        else:
            self.rank = None
            self.suffix = ''

        self.data_names = defaultdict(list)  # tag -> set[str]

    @staticmethod
    def _write_line(f, lst):
        for i, e in enumerate(lst):
            f.write(str(e))
            if i + 1 < len(lst):
                f.write('\t')
        f.write('\n')

    def log_numbers(self, numbers: dict, global_step=None, epoch=None, tag=None):
        if tag is None:
            fname = 'default'
        else:
            fname = tag.replace('\\', '_').replace('/', '_')
        with open(os.path.join(self.outputs_dir, fname + self.suffix + '.tsv'), 'a') as f:
            if set(self.data_names[tag]) != set(numbers.keys()):
                self.data_names[tag] = list(numbers.keys())
                self.__class__._write_line(
                    f, ['global_step', 'epoch'] + self.data_names[tag])

            values = [global_step, epoch] + [numbers[name]
                                             for name in self.data_names[tag]]
            self.__class__._write_line(f, values)


class TensorBoardLogger(Logger):
    def __init__(self, _ctx):
        self.context = _ctx

    def setup(self, outputs_dir):
        from torch.utils.tensorboard import SummaryWriter
        self.outputs_dir = outputs_dir

        if not dist.is_initialized() or dist.get_rank() == 0:
            if hasattr(self.context, '_tensorboard_log_dir'):
                log_dir = self.context._tensorboard_log_dir
            else:
                log_dir = self.outputs_dir
            os.makedirs(log_dir, exist_ok=True)
            self.writer = SummaryWriter(log_dir=log_dir)
        else:
            self.writer = None

    def log_numbers(self, numbers: dict, global_step=None, epoch=None, tag=None):
        if self.writer is not None:
            if global_step is not None:
                for name, val in numbers.items():
                    self.writer.add_scalar(
                        f'by_global_step/{_tagged(name, tag)}', val, global_step=global_step)
            if epoch is not None:
                for name, val in numbers.items():
                    self.writer.add_scalar(
                        f'by_epoch/{_tagged(name, tag)}', val, global_step=epoch)
