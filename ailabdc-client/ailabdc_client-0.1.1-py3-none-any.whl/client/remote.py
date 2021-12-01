import time
import requests
import urllib.request as urllib_request
import requests
from io import BytesIO

import numpy as np
from PIL import Image

from .func import *

__all__ = ["get_file_io", "get_img_file", "get_numpy_file", "get_text_file"]

def get_file_io(url, retry=1, retry_gap=1, proxy=None) -> BytesIO:
    proxies = {'http': proxy, 'https': proxy} if proxy else {}
    try:
        current_client = get_ssh_info().to_dict()
        r = requests.post(url, json={'client': current_client}, proxies=proxies, stream=True)
        byteIOObj = BytesIO()
        if r.status_code == 200:
            for chunk in r:
                byteIOObj.write(chunk)
            return byteIOObj
        else:
            raise Exception(f"Can't download file: {r.text} abc")
    except Exception as e:
        if retry > 0:
            time.sleep(retry_gap)
            return get_file_io(url, retry=retry-1, proxy=proxy)
        else:
            raise e

def get_img_file(url) -> Image:
    byte = get_file_io(url)
    img = Image.open(byte)
    return img

def get_numpy_file(url) -> np.ndarray:
    byte = get_file_io(url)
    arr = np.load(byte)
    return arr

def get_text_file(url) -> str:
    byte = get_file_io(url)
    return byte.readlines()