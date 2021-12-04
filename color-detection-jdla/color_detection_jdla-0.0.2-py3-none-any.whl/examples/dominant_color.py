from color_detection.detect import Mask
from PIL import Image, ImageColor
import numpy as np
import colors
import cv2

# Read Image
myarray = cv2.imread("img/red.jpg")

# Detect dominant color
color = Mask.detect_dominant(myarray)

# np.array to PIL Image
image = Image.fromarray(myarray)

# Create image
pil_image = Image.new('RGB', (1, 1), color=color)

# PIL Image to np.array
np_image = np.array(pil_image)

print(color)
