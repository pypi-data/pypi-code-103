from color_detection.detect import Mask
import numpy as np
import unittest
import colors
import cv2

# Run file: python -m test.test_color_detection


class TestColorDetection(unittest.TestCase):

    def test_dominant_color(self):

        # Read Image
        image = cv2.imread("img/blue.jpg")

        # Detected color
        color = Mask.detect_dominant(image)

        self.assertEqual(color, (196, 92, 4))

    def test_detect_color(self):
        # Test mask
        my_mask = Mask("Blue", colors.BLUE["lower"], colors.BLUE["upper"])

        # Test Color
        color = (196, 92, 4)

        detected_mask = Mask.detect(color, [my_mask])

        self.assertEqual(detected_mask, my_mask)


if __name__ == "__main__":
    unittest.main()
