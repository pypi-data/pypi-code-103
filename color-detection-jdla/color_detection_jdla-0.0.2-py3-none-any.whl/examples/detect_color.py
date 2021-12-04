from color_detection.detect import Mask
import numpy as np
import colors
import cv2


def selectImage(source, height, width):
    # Using image
    image = cv2.imread(source)
    image = cv2.resize(image, (width, height))


blue = Mask("Azul", colors.BLUE["lower"], colors.BLUE["upper"])
green = Mask("Verde", colors.GREEN["lower"], colors.GREEN["upper"])
orange = Mask("Naranja", colors.ORANGE["lower"], colors.ORANGE["upper"])
red_light = Mask("Rojo", colors.LIGHT_RED["lower"], colors.LIGHT_RED["upper"])
red_dark = Mask("Rojo", colors.DARK_RED["lower"], colors.DARK_RED["upper"])
yellow = Mask("Amarillo", colors.YELLOW["lower"], colors.YELLOW["upper"])
white = Mask("Blanco", colors.WHITE["lower"], colors.WHITE["upper"])
colors = [blue, green, orange, red_light, red_dark, yellow, white]

image = cv2.imread("img/red.jpg")
color = Mask.detect_dominant(image)

detected_color = Mask.detect(color, colors)
print(detected_color.name)

cv2.imshow("contour", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
