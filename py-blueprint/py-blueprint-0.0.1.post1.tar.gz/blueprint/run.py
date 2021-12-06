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

import argparse
from . import build, Context, get_user_config


def _main():
    parser = argparse.ArgumentParser()

    parser.add_argument('job_cfg', type=str,
                        help='The experiment configuration file (.yaml) ')

    parser.add_argument('--exp_name', type=str, default=None)
    parser.add_argument('--blob_root', type=str, default=None)
    parser.add_argument('--copy2local', type=int, default=0)
    parser.add_argument('--debug_loss', type=int, default=1)
    parser.add_argument('--detect_anomaly', type=int, default=1)
    args, _other_args = parser.parse_known_args()

    other_args = dict()
    for idx in range(0, len(_other_args), 2):
        key = _other_args[idx]
        val = _other_args[idx+1]
        assert key.startswith('--')
        key = key[2:]
        other_args[key] = val

    exp_name = args.exp_name
    if exp_name is None:
        exp_name = get_user_config('exp_name', 'default_experiment')

    blob_root = args.blob_root
    if blob_root is None:
        blob_root = get_user_config('blob_root', './blob')

    print(f'====== RUNNING {args.job_cfg} ======')
    runnable = build(Context(exp_name=exp_name, blob_root=blob_root,
                             copy2local=args.copy2local == 1,
                             debug_loss=args.debug_loss == 1,
                             detect_anomaly=args.detect_anomaly == 1),
                     args.job_cfg, **other_args)
    runnable()


if __name__ == '__main__':
    _main()
