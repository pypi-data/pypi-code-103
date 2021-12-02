import logging
import subprocess
from os import path


def convert_gif(assets_folder: str, gif_filename: str):
    filename, _ = path.splitext(gif_filename)
    try:
        CMD = f"convert {path.join(assets_folder, gif_filename)}[0] {path.join(assets_folder, filename)}.png"
        logging.info(f"running: {CMD}")
        subprocess.run(CMD, shell=True, check=True)
    except subprocess.CalledProcessError as err:
        logging.error(f"Error: {CMD}")
        logging.error(str(err))
        raise ValueError(f"Error during: {CMD}") from err
    return f"{filename}.png"
