#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
See links for OCR details
https://github.com/UB-Mannheim/tesseract/wiki
https://digi.bib.uni-mannheim.de/tesseract/
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

import ast
import os
import platform
import pytesseract
import shutil
import sys
from ..Other import convert_character
from ..Shell import print_error
from PIL import Image, ImageDraw, ImageFont, ImageFile, PngImagePlugin, BmpImagePlugin
from io import BytesIO
from platform import architecture
from tempfile import gettempdir

OCR_WEB_LINK = 'https://digi.bib.uni-mannheim.de/tesseract/'
OCR_PATH = None

if sys.platform.startswith('win') and architecture()[0] == '64bit':
    if os.path.exists(os.sep.join([os.environ["ProgramFiles"], 'Tesseract-OCR', 'tesseract.exe'])):
        OCR_PATH = os.sep.join([os.environ["ProgramFiles"], 'Tesseract-OCR', 'tesseract.exe'])
    OCR_WEB_LINK += 'tesseract-ocr-w64-setup-v5.0.0-alpha.20210506.exe'
elif sys.platform.startswith('win') and architecture()[0] == '32bit':
    if os.path.exists(
            os.sep.join([os.environ["ProgramFiles(x86)"], 'Tesseract-OCR', 'tesseract.exe'])
    ):
        OCR_PATH = os.sep.join([os.environ["ProgramFiles(x86)"], 'Tesseract-OCR', 'tesseract.exe'])
    OCR_WEB_LINK += 'tesseract-ocr-w32-setup-v5.0.0-alpha.20210506.exe'
elif sys.platform.startswith('linux'):
    OCR_PATH = True

if os.path.exists(os.sep.join([os.path.dirname(gettempdir()), 'Tesseract-OCR', 'tesseract.exe'])):
    OCR_PATH = os.sep.join([os.path.dirname(gettempdir()), 'Tesseract-OCR', 'tesseract.exe'])

ImageFile.LOAD_TRUNCATED_IMAGES = True


# noinspection PyBroadException
class Photo:
    def __init__(self):
        self.mode = 'RGB'
        self.width = 960
        self.height = 540

        self.image_path_master = None
        self.image_path_grab = None
        self.image_path_diff = None
        self.image_path_mask = None

        self.image_data_master = None
        self.image_data_grab = None
        
    def compare_images_from_image(self, master=None, received=None, mask_coordinates=None):
        if (
                isinstance(master, bytes) and
                len(master) != 0 and
                isinstance(received, bytes) and
                len(received) != 0
        ):
            try:
                self.image_path_master = BytesIO(master)
                self.image_path_grab = BytesIO(received)
                if mask_coordinates not in (None, 'None'):
                    mask_name, mask_coordinates = self.create_mask(
                        None, ast.literal_eval(mask_coordinates)
                    )
                    mask_coordinates.load()
                else:
                    mask_coordinates = None
                self.images_read(convert=False)
                return self.compare_image(
                    self.image_data_master, self.image_data_grab, mask_coordinates
                )
            except Exception as error:
                print_error(error, locals())
        return None, None

    def image_crop(self, image, crop_coordinate=None):
        print(f'Image Crop: #{crop_coordinate}#')
        try:
            if (
                    crop_coordinate is not None and
                    isinstance(crop_coordinate, list) and
                    len(crop_coordinate) == 4
            ):
                (left, upper, right, lower) = crop_coordinate
                image = self.images_check(image).crop((left, upper, right, lower))
                print(f'Clipping was performed successfully --->{crop_coordinate}')
        except Exception as error:
            print_error(error, locals())
        return image

    def convert_image_to_txt_with_ocr(self, data, crop_coordinate=None, lang='eng'):
        try:
            if platform.system() == 'Windows':
                pytesseract.pytesseract.tesseract_cmd = OCR_PATH
            img = self.images_check(data)
            if crop_coordinate is not None and isinstance(crop_coordinate, list):
                img = self.image_crop(img, crop_coordinate=crop_coordinate)
            os.environ["TESSDATA_PREFIX"] = os.path.join(os.path.dirname(OCR_PATH), 'tessdata')
            txt = pytesseract.image_to_string(img, lang=lang).rstrip()
            print(f'OCR read operation successful. String:#{txt}#')
            return txt
        except Exception as error:
            print_error(error, locals())
            return None

    @staticmethod
    def image_read(path):
        image = None
        try:
            if os.path.exists(str(path)):
                with open(path, 'rb') as f:
                    image = Image.open(f)
                    image.load()
                f.close()
        except Exception as error:
            print_error(error, locals())
        finally:
            return image

    def image_convert(self, data):
        try:
            if data.mode == 'RGBA':
                new = Image.new(self.mode, data.size, (255, 255, 255))
                new.paste(data, mask=data.split()[3])
                data = new.copy()
                new.close()
            else:
                data = data.convert(self.mode).resize((self.width, self.height))
            data.load()
        except Exception as error:
            print_error(error, locals())
        return data

    @staticmethod
    def image_show(data):
        try:
            data.show()
        except Exception as error:
            print_error(error, locals())

    def images_check(self, data=None, blank_image_color=None, convert=False):
        try:
            if isinstance(data, BytesIO):
                data = Image.open(data)
            elif isinstance(data, bytes) and len(data) != 0:
                data = Image.open(BytesIO(data))
            elif isinstance(data, str) and os.path.exists(path=data):
                data = self.image_read(data)
            elif (
                    isinstance(data, Image.Image) or
                    type(data) == ImageFile or
                    isinstance(data, PngImagePlugin.PngImageFile) or
                    isinstance(data, BmpImagePlugin.BmpImageFile)
            ):
                pass
            else:
                blank_image_color = 'red' if blank_image_color is None else blank_image_color
                data = Image.new(self.mode, (self.width, self.height), blank_image_color)
            if convert:
                data = self.image_convert(data)
            data.load()
        except Exception as error:
            print_error(error, locals())
        return data.copy()

    def image_save(
            self, data, path=None, message=None, transpose=None,
            blank_image_color=None, convert=True
    ):
        try:
            byte_io = None
            data = self.images_check(data, blank_image_color=blank_image_color, convert=convert)
            if data is not None:
                if transpose is not None:
                    if transpose == 'FLIP_LEFT_RIGHT':
                        data = data.transpose(Image.FLIP_LEFT_RIGHT)
                    elif transpose == 'FLIP_TOP_BOTTOM':
                        data = data.transpose(Image.FLIP_TOP_BOTTOM)
                    elif transpose == 'ROTATE_90':
                        data = data.transpose(Image.ROTATE_90)
                    elif transpose == 'ROTATE_180':
                        data = data.transpose(Image.ROTATE_180)
                    elif transpose == 'ROTATE_270':
                        data = data.transpose(Image.ROTATE_270)
                    elif transpose == 'TRANSPOSE':
                        data = data.transpose(Image.TRANSPOSE)
                    elif transpose == 'TRANSVERSE':
                        data = data.transpose(Image.TRANSVERSE)
                if path is not None:
                    try:
                        data.save(path)
                    except IOError as error:
                        print(f'-------> Image write problem:{error}')
                byte_io = BytesIO()
                data.save(byte_io, 'PNG')
                data.close()
                del data
            if message is not None:
                print(f'-------> Write Operation Successful -------> {message}')
            return True, byte_io, None
        except Exception as error:
            print_error(error, locals())
            return False, None, error

    def combine_several_images(self, image_list):
        result = None
        try:
            if len(image_list) > 1:
                result = Image.new(self.mode, (self.width * 2, self.height * 2))
                for i, data in enumerate(image_list):
                    img = self.images_check(data, blank_image_color='red', convert=False)
                    img.thumbnail((self.width, self.height), Image.ANTIALIAS)
                    x, y = i // 2 * self.width, i % 2 * self.height
                    w, h = img.size
                    result.paste(img, (x, y, x + w, y + h))
                result.load()
            else:
                result = self.images_check(image_list[0], convert=False)
                result.load()
        except Exception as error:
            print_error(error, locals())
        return result

    def create_mask(self, mask_name=None, coordinates=None):
        img_base = None
        try:
            if coordinates[-1] == 'Invert':
                invert, invert_img_base, invert_type = True, 'black', 'white'
                xy_value = len(coordinates) - 1
            else:
                invert, invert_img_base, invert_type = False, 'white', 'black'
                xy_value = len(coordinates)
            img_base = Image.new(self.mode, (self.width, self.height), invert_img_base)
            for i in range(xy_value):
                try:
                    xi, yi, xf, yf = coordinates[i]
                    img_base.paste(Image.new(self.mode, (xf - xi, yf - yi), invert_type), (xi, yi))
                except ValueError as e:
                    print(f'-------> CreateMask Error Name:{mask_name}')
                    print(f'Coordinates:{coordinates} Errors:{e}')
            img_base.load()
            self.image_save(img_base, mask_name, f'Mask Picture Created:{mask_name}')
        except Exception as error:
            print_error(error, locals())
        return mask_name, img_base

    def create_image_with_text(self, text='Failed to grab image from TV.'):
        try:
            text_new = ''
            for t in str(text).split('\n'):
                text_swap = ''
                for i, ch in enumerate(str(t)):
                    text_swap += ch + ('\n' if i % 33 == 0 and i != 0 else '')
                text_new += text_swap + '\n'
            font = ImageFont.load_default()
            image = Image.new('RGB', (self.width, self.height), "black")
            draw = ImageDraw.Draw(image)
            draw.text(
                ((self.width / 2) - 66 - 10, self.height / 2 - ((len(text) / 33) * 2) - 10),
                text_new,
                'white',
                font
            )
            image.load()
            del draw
        except Exception as error:
            print(f'****************************************************************************')
            print(f'*** Error! create_image_with_text ---> {error}')
            print(f'****************************************************************************')
            image = Image.new('RGB', (self.width, self.height), "red")
            image.load()
        return image

    def __difference(self, grabbed_image, master_image):
        grabbed_data = grabbed_image.getdata()
        master_data = master_image.getdata()
        difference_image = None
        images_match = True
        for i in range(len(grabbed_data)):
            (grab_r, grab_g, grab_b) = grabbed_data[i]
            (master_r, master_g, master_b) = master_data[i]
            images_match = (grab_r == master_r) and (grab_g == master_g) and (grab_b == master_b)
            if not images_match:
                break
        if not images_match:
            difference_image = Image.new(self.mode, master_image.size)
            difference_data = [None] * len(grabbed_data)
            for i in range(len(grabbed_data)):
                grab_r, grab_g, grab_b = grabbed_data[i]
                master_r, master_g, master_b = master_data[i]
                is_different = not (
                        (grab_r == master_r) and
                        (grab_g == master_g) and
                        (grab_b == master_b)
                )
                if is_different:
                    diff = (255, 0, 0)
                else:
                    diff = (255, 255, 255)
                # noinspection PyTypeChecker
                difference_data[i] = diff
            difference_image.putdata(difference_data)
            difference_image.load()
        return images_match, difference_image

    def __difference_with_mask(self, grabbed_image, master_image, mask_image):
        grabbed_data = grabbed_image.getdata()
        master_data = master_image.getdata()
        mask_data = mask_image.getdata()
        difference_image = None
        images_match = True
        for i in range(len(grabbed_data)):
            (grab_r, grab_g, grab_b) = grabbed_data[i]
            (master_r, master_g, master_b) = master_data[i]
            is_different = not (
                    (grab_r == master_r) and
                    (grab_g == master_g) and
                    (grab_b == master_b)
            )
            if is_different:
                (mask_r, mask_g, mask_b) = mask_data[i]
                is_masked = (mask_r != 255) or (mask_g != 255) or (mask_b != 255)
                if not is_masked:
                    images_match = False
                    break
        if not images_match:
            difference_image = Image.new(self.mode, master_image.size)
            difference_data = [None] * len(grabbed_data)
            for i in range(len(grabbed_data)):
                (grab_r, grab_g, grab_b) = grabbed_data[i]
                (master_r, master_g, master_b) = master_data[i]
                (mask_r, mask_g, mask_b) = mask_data[i]
                is_different = not (
                        (grab_r == master_r) and
                        (grab_g == master_g) and
                        (grab_b == master_b)
                )
                is_masked = (mask_r != 255) or (mask_g != 255) or (mask_b != 255)
                if is_different and is_masked:
                    diff = (255, 0, 255)
                elif is_different:
                    diff = (255, 0, 0)
                    images_match = False
                elif is_masked:
                    diff = (0, 0, 255)
                else:
                    diff = (255, 255, 255)
                # noinspection PyTypeChecker
                difference_data[i] = diff
            difference_image.putdata(difference_data)
            difference_image.load()
        return images_match, difference_image

    def compare_image(self, master, grabbed, mask):
        if mask is not None:
            result, difference = self.__difference_with_mask(grabbed, master, mask)
        else:
            result, difference = self.__difference(grabbed, master)

        if not result:
            self.image_save(
                difference,
                self.image_path_diff,
                f'Diff Picture Created:{self.image_path_diff}'
            )
        return result, difference

    def images_read(self, convert=False):
        self.image_data_master = self.images_check(self.image_path_master, convert=convert)
        self.image_data_grab = self.images_check(self.image_path_grab, convert=convert)
        mask = self.image_read(self.image_path_mask)
        return self.image_data_master, self.image_data_grab, mask

    def screen_matches(
            self, specific, sub_name, mask, does_not_match,
            path_result, path_master, path_master_common, path_master_public
    ):
        result_boolean = None
        try:
            if specific is None:
                self.image_path_master = os.path.join(path_master, f'{sub_name}.png')
            elif specific == 'Public of the Project':
                self.image_path_master = os.path.join(path_master_public, f'{sub_name}.png')
            elif isinstance(specific, list) and len(specific) == 2:
                self.image_path_master = os.path.join(
                    path_master_public, convert_character(str(specific[-1]).replace(' ', '_'), '.')
                )
            elif os.path.exists(specific):
                if specific[-9:] != '__ref.png':
                    self.image_path_master = f'{specific[:-4]}__ref.png'
                if not os.path.exists(self.image_path_master):
                    try:
                        try:
                            shutil.copytree(specific, self.image_path_master)
                        except Exception:
                            shutil.copy2(specific, self.image_path_master)
                        print(f':::::> COPY SUCCESS: {specific} ---> {self.image_path_master}')
                    except Exception as error:
                        print(
                            f':::::> COPY PROBLEM!: {specific} '
                            f'---> {self.image_path_master} :::> {error}'
                        )
            elif specific == 'Video':
                self.image_path_master = os.path.join(path_result, 'Video_REF.png')
                self.image_save(self.images_check(
                    blank_image_color='black'), self.image_path_master, convert=True
                )
            else:
                self.image_path_master = os.path.join(
                    path_master_common, convert_character(str(specific).replace(' ', '_'), '.')
                )

            self.image_path_grab = os.path.join(path_result, f'{sub_name}.png')
            self.image_path_diff = None
            if mask is None:
                self.image_path_mask = None
            else:
                self.image_path_mask, img_base = self.create_mask(
                    f'{self.image_path_grab[:-4]}_MASK.png', mask
                )
            if (
                    not os.path.exists(self.image_path_master) or
                    os.path.getsize(self.image_path_master) == 0
            ):
                print(f'-------> # Master Picture NONE! # Master Path:{self.image_path_master}')
            elif (
                    not os.path.exists(self.image_path_grab) or
                    os.path.getsize(self.image_path_grab) == 0
            ):
                print(f'-------> # Result Picture NONE! # Result Path:{self.image_path_grab}')
            else:
                self.image_path_diff = f'{self.image_path_grab[:-4]}_diff.png'
                master, grabbed, mask = self.images_read(convert=True)
                result_boolean, difference = self.compare_image(master, grabbed, mask)
                if master is not None:
                    master.close()
                if grabbed is not None:
                    grabbed.close()
                if mask is not None:
                    mask.close()
                if does_not_match:
                    print(f'Picture Compare Does Not Match Before:{sub_name} :::>{result_boolean}')
                    result_boolean = False if result_boolean else True
                del master, grabbed, mask, difference
            print(f'-------> Picture Compare: Master Path:{self.image_path_master}')
            print(f'-------> Picture Compare: Result Path:{self.image_path_grab}')
            print(f'-------> Picture Compare: {sub_name} :::> : {result_boolean}')
        except Exception as error:
            print_error(error, locals())
        return [
            sub_name,
            result_boolean,
            self.image_path_master,
            self.image_path_grab,
            self.image_path_mask,
            self.image_path_diff,
            self.image_path_master,
            self.image_path_grab
        ]
