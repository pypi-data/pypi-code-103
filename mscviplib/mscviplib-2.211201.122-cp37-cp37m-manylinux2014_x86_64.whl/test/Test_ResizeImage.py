import mscviplib
import numpy as np
import unittest

from os import path
from PIL import Image

class Test_ResizeImage(unittest.TestCase):
    def runTest(self):
        print("\nStarting Test_ResizeImage")

        root = path.dirname(path.abspath(__file__))

        test_image_filename = path.join(root, "test.jpg")
        image = Image.open(test_image_filename)
        metadata = mscviplib.GetImageMetadata(image)
        target_size = (224, 224)

        try:
            print("calling PreprocessForInferenceAsImage!")
            resized_image = mscviplib.PreprocessForInferenceAsImage(metadata, 
                                                    image.tobytes(), 
                                                    mscviplib.ResizeAndCropMethod.CropCenter, 
                                                    (224, 224), 
                                                    mscviplib.InterpolationType.Bilinear, 
                                                    mscviplib.ColorSpace.RGB)
        except Exception as e:
           self.fail("unittest.main()'Test_ResizeImage' unexpectedly failed!  exception: " + str(e))

        self.assertIsNotNone(resized_image, msg="PreprocessForInferenceAsImage returned None!")
        self.assertIsInstance(resized_image, np.ndarray, msg="PreprocessForInferenceAsImage returned results are NOT of type np.ndarray!")

        self.assertEqual(resized_image.shape[0], 224, msg="Height should have been 224!")
        self.assertEqual(resized_image.shape[1], 224, msg="Width should have been 224!")
        self.assertEqual(resized_image.shape[2], 3, msg="Number of Channels should have been 3!")
        print("ResizeImage returned image with the correct size!")


if __name__ == '__main__':
    unittest.main()
