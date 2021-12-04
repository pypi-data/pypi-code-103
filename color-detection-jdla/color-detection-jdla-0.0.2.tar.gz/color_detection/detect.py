from __future__ import annotations
from colorthief import ColorThief
from PIL import Image
import numpy as np
import colorsys
import cv2
import io

"""Detect dominant color of a OpenCV frame."""


class Mask:
    """Mask main class."""

    def __init__(self, name: str, color_lower: list, color_upper: list):
        """Create a new color mask.

        Args:
            name (str): the name of the color.
            color_lower (list): hsv lower boundry.
            color_upper (list): hsv upper boundry.
        """
        self.name = name
        self.color_lower = color_lower
        self.color_upper = color_upper

    @property
    def get_RGB(self) -> tuple:
        """Get RGB value of Mask

        Returns:
            tuple: rgb lower boundry.
            tuple: rgb lower boundry.
        """
        lower_rgb = colorsys.hsv_to_rgb(
            self.color_lower[0], self.color_lower[1], self.color_lower[2])
        upper_rgb = colorsys.hsv_to_rgb(
            self.color_upper[0], self.color_upper[1], self.color_upper[2])
        return lower_rgb, upper_rgb

    @staticmethod
    def detect(rgb_color: tuple, masks: list) -> Mask:
        """Detect color.

        Args:
            rgb_color: rgb color to detect.
            masks: list of colors (Masks).

        Returns:
            Mask: detected Mask color.
        """
        # Create image
        pil_image = Image.new('RGB', (1, 1), color=rgb_color)

        # PIL Image to np.array
        color = np.array(pil_image)

        hsv = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)

        for mask in masks:
            temporal_mask = cv2.inRange(hsv, np.array(mask.color_lower),
                                        np.array(mask.color_upper))

            if(np.count_nonzero(temporal_mask) != 0):
                color = mask
                break

        if type(color) is not Mask:
            raise Exception("Color not found.")

        return color

    @staticmethod
    def detect_dominant(frame: np.ndarray) -> tuple:
        """Detect dominant color of a OpenCV frame.

        Args:
            frame (np.ndarray): OpenCV frame.

        Returns:
            tuple: rgb dominant color.
        """

        # Frame to image
        image = Image.fromarray(frame)

        # Image to file
        byte_object = io.BytesIO()
        image.save(byte_object, 'JPEG')

        color_thief = ColorThief(byte_object)
        dominant_color = color_thief.get_color(quality=1)

        return dominant_color
