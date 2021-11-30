import os
import sys
import math
from pathlib import Path

from fad.constants import PAGE_ANCHOR_SELECTOR, USER_ANCHOR_SELECTOR, GROUP_ANCHOR_SELECTOR

HOME = Path.home()

def get_anchor_selector(type):
    selectors = {
        'user': USER_ANCHOR_SELECTOR,
        'group': GROUP_ANCHOR_SELECTOR,
        'page': PAGE_ANCHOR_SELECTOR,
    }
    return selectors.get(type, None)

def get_default_config_path():
    return HOME / '.config' / 'fad' / 'config.json'

def get_downloads_dir():
    return HOME / 'Downloads'

def get_driver_executable_path():
    return HOME / '.local' / 'bin' / 'geckodriver'

def create_save_directory(dir, album_name):
    save_dir = Path(dir) / album_name
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    return save_dir

def progressbar(amount, total, prefix='Progress: ', size=50):
    console = sys.stdout
    percentage = round((100 * amount) / total, 2) 
    factor = total / size
    num_of_progress_chars = math.floor(amount / factor)
    num_of_space_chars = size - num_of_progress_chars
    bar = '\u2588' * num_of_progress_chars + ' ' * num_of_space_chars 
    # print progressbar
    console.write('\r%s\u2502%s\u2502  %.2f%s ...... %i/%i\r' % (prefix, bar, percentage, '%', amount, total))
    console.flush()

def convert_title(title):
    special_chars = '@-_!#$%^&*()<>?/\\|}{~:;[].,'
    clean_title = ''.join(c for c in title.split('|')[0] if not c in special_chars).strip()
    return '-'.join(clean_title.split(' '))
