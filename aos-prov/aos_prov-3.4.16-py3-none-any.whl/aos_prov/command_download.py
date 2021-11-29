#
#  Copyright (c) 2018-2021 Renesas Inc.
#  Copyright (c) 2018-2021 EPAM Systems Inc.
#

import sys
from pathlib import Path

import requests

DOWNLOADS_PATH = Path.home() / '.aos' / 'downloads'


def _download_and_save(url: str, file_name: str):
    DOWNLOADS_PATH.mkdir(parents=True, exist_ok=True)
    full_path = DOWNLOADS_PATH / file_name
    with open(full_path, 'wb') as f:
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                sys.stdout.flush()
    return full_path


def download_image(address: str = 'https://epam-my.sharepoint.com/:u:/p/volodymyr_mykytiuk1/ERK4_JGBmGJApEwupIlxq7sBaU-hqEyxJbACTsiP8KP9qw?e=cK2hfi&download=1'):
    Path(DOWNLOADS_PATH).mkdir(parents=True, exist_ok=True)
    print("Downloading Aos core image...")
    return _download_and_save(address, 'aos-disk.vmdk')


def download_vbox_sdk():
    download_path = 'https://download.virtualbox.org/virtualbox/6.1.30/VirtualBoxSDK-6.1.30-148432.zip'
    print("Downloading VirtualBox SDK...")
    return _download_and_save(download_path, 'vox-sdk.zip')
