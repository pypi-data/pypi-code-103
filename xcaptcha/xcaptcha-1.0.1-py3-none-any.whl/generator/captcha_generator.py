import cv2 as cv
from itertools import product
import numpy as np
from numpy.random import randint
from typing import Callable, List, Tuple

from xcaptcha.types import CAPTCHA


class CAPTCHAGenerator():
    def __init__(self, charset: str, min_size: Tuple[int, int], max_size: Tuple[int, int],
                 min_length: int, max_length: int, fonts: List[str]):
        self.charset = charset
        self.charset_length = len(self.charset)
        self.min_size = min_size
        self.max_size = max_size
        self.min_length = min_length
        self.max_length = max_length
        self.fonts = fonts

    def __iter__(self):
        return self

    def __next__(self) -> CAPTCHA:
        return self.generate()

    def generate(self) -> CAPTCHA:
        n_chars = randint(self.min_length, high=self.max_length + 1)
        text = [self.charset[i]
                for i in randint(0, high=self.charset_length, size=(n_chars,))]
        height = randint(self.min_size[0], high=self.max_size[0] + 1)
        width = randint(self.min_size[1], high=self.max_size[1] + 1)

        canvas = np.ones((height, width, 4), dtype=np.uint8) * 255
        character_masks = {}

        # Draw random dots in image
        for _ in range(0, randint(20, 31)):
            canvas = self._draw_dot(canvas, width, height)

        # Generate characters
        for i in range(len(text)):
            # Generate text layer for character
            layer = self._make_char_layer(i, text[i], n_chars, width, height)

            # Character mask
            character_masks[text[i]] = self._mask_from_layer(
                layer, width, height)

            # Overlay this layer onto canvas
            canvas = self._merge_layers(canvas, layer)

        # Draw random lines over image
        for _ in range(0, randint(7, 14)):
            canvas = self._draw_line(canvas, width, height)

        # Remove alpha channel
        canvas = canvas[:, :, :3]

        return CAPTCHA(canvas, character_masks, text)

    def merge_masks(self, masks: np.ndarray, upper_sentinel: int = 1):
        merged = masks[0]
        for i in range(len(masks) - 1):
            bottom = merged
            top = masks[i + 1]
            merged = np.where(top == upper_sentinel, top, bottom)
        return merged

    def _get_char_pos(self, i: int, width: int, height: int, n_chars: int):
        return (width // (n_chars + 6) + width * i // (n_chars + 1), height * n_chars // (n_chars + 4))

    def _get_next_font(self, c: str):
        # Not everyone can read cursive well, and f, b, and z in these cursive
        # fonts look especially different from their script counterparts
        return self.fonts[randint(0, len(self.fonts[:-2] if c in ["f", "b", "z"] else self.fonts))]

    def _get_next_font_scale(self):
        return randint(2, 4)

    def _get_next_color(self):
        return tuple([randint(0, 256) for _ in range(3)]) + (255,)

    def _get_next_thickness(self):
        return randint(2, 5)

    def _get_rotate_mat(self, i: int, width: int, height: int, n_chars: int):
        char_pos = list(self._get_char_pos(i, width, height, n_chars))
        char_pos[0] += width // (n_chars + 4)
        return cv.getRotationMatrix2D(center=tuple(char_pos), angle=randint(-45, 45), scale=1)

    def _get_position(self, width: int, height: int):
        return (randint(0, width), randint(0, height))

    def _draw_line(self, canvas: np.ndarray, width: int, height: int):
        start = self._get_position(width, height)
        end = self._get_position(width, height)
        return cv.line(canvas, start, end, self._get_next_color()[:3], 1)

    def _draw_dot(self, canvas: np.ndarray, width: int, height: int):
        return cv.circle(canvas, self._get_position(width, height), randint(0, 6), self._get_next_color()[:3], thickness=randint(-1, 2))

    def _make_char_layer(self, i: int, char: str, n_chars: int, width: int, height: int):
        layer = np.zeros((height, width, 4), dtype=np.uint8)
        cv.putText(layer, char, self._get_char_pos(
            i, width, height, n_chars), self._get_next_font(char), self._get_next_font_scale(), self._get_next_color(), self._get_next_thickness())
        layer = cv.warpAffine(layer, self._get_rotate_mat(
            i, width, height, n_chars), (width, height))
        return layer

    def _merge_layers(self, bottom: np.ndarray, top: np.ndarray):
        # https://stackoverflow.com/a/59211216/14226597
        # Normalize alpha channels from 0-255 to 0-1
        alpha_background = bottom[:, :, 3] / 255.0
        alpha_foreground = top[:, :, 3] / 255.0

        # Set adjusted colors
        for color in range(0, 3):
            bottom[:, :, color] = alpha_foreground * top[:, :, color] + \
                alpha_background * bottom[:, :, color] * (1 - alpha_foreground)

        # Set adjusted alpha and denormalize back to 0-255
        bottom[:, :, 3] = (1 - (1 - alpha_foreground) *
                           (1 - alpha_background)) * 255

        return bottom

    def _mask_from_layer(self, layer: np.ndarray, width: int, height: int, sentinel: int = 1):
        mask = np.zeros((height, width), dtype=np.float32)
        for coordinates in product(range(height), range(width)):
            if not (layer[coordinates] == 0).all():
                mask[coordinates] = sentinel
        return mask
