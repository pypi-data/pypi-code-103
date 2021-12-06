from io import BytesIO
from typing import Tuple

from PIL import Image


def apply_alpha(img: Image, alpha: float) -> Image:
    r, g, b, a = img.split()

    def lut(pixel: int) -> int:
        return int(pixel * alpha)

    a = a.point(lut)

    return Image.merge('RGBA', [r, g, b, a])


class Renderer:
    ''' Manages the render into an image, used to abstract the library used for
    drawing, so it can be easily replaced, upgraded or fixed '''

    def __init__(self, width, height):
        self.image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        self.width = width
        self.height = height

    def paste(self, image: bytes, box: Tuple[int, int] = (0, 0), alpha: float = 1.0):
        img = Image.open(BytesIO(image))

        img_with_alpha = apply_alpha(img, alpha)

        self.image.paste(img_with_alpha, box=box)

    def alpha_composite(self, image: bytes, alpha: float = 1.0):
        img = Image.open(BytesIO(image))
        img_with_alpha = apply_alpha(img, alpha)
        self.image = Image.alpha_composite(self.image, img_with_alpha)

    def getpixel(self, pixel: Tuple[int, int]) -> Tuple[int, int, int, int]:
        return self.image.getpixel(pixel)

    def get_image(self) -> Image:
        return self.image.copy()

    def get_png_bytes(self) -> BytesIO:
        fp = BytesIO()
        self.image.save(fp, format='png')

        return fp

    def save(self, filename: str):
        self.image.save(filename)
