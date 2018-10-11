from django.test import TestCase
from PIL import Image
import os

from .tagger import detect

class TaggerTests(TestCase):
    
    def test_tagger_initialized_successfully(self):
        self.assertTrue(True)
    
    # TODO break up this multiple tests that check specific tag values returned by detect
    def test_process_test_images(self):
        print(os.listdir('imageprocessor/tagservice/test_images'))
        self.assertTrue(True)

        # Get the file name for every image in the test_images folder
        TEST_IMAGE_NAMES = [f for f in os.listdir('imageprocessor/tagservice/test_images') if os.path.isfile(os.path.join('imageprocessor/tagservice/test_images', f))]

        # load images and perform detection
        for image_name in TEST_IMAGE_NAMES:
            image = Image.open(os.path.join('imageprocessor/tagservice/test_images', image_name))
            print("Successfully loaded image " + image_name if image else "Failed to load image " + image_name)

            list_of_tags = ', '.join(map(str, detect(image)))
            print('Detection Complete for {}:\n[{}] \n'.format(image_name, list_of_tags))

            self.assertIsNotNone(image)
            self.assertTrue(list_of_tags)
    
    # more unit tests here