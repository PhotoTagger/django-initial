from builtins import ValueError

from django.test import TestCase, Client
from PIL import Image
from django.urls import reverse
from imageprocessor.tests import delete_test_images, TEST_IMAGES_DIR
import os

from .tagger import detect



class TaggerTests(TestCase):

    def test_tagger_initialized_successfully(self):
        self.assertTrue(True)

    def test_can_read_files_from_dir(self):
        test_image_files= os.listdir(TEST_IMAGES_DIR)
        self.assertTrue("image1.jpg" in test_image_files)
        print("Verifying access to images in test directory: {}\n".format(pretty_print_tags(test_image_files)))

    def test_ability_to_open_images(self):
        image_name = "image3.jpg"

        image = open_image(image_name)
        self.assertIsNotNone(image, "Failed to load image")

    def test_detect_cats_and_dogs(self):
        # load images and perform detection
        image_name = "image3.jpg"
        image = open_image(image_name)

        tags = detect(image)
        print('Detection Complete for {}:\ntags:{} \n'.format(image_name, pretty_print_tags(tags)))

        self.assertTrue(len(tags) == 2)
        self.assertTrue("dog" in tags)
        self.assertTrue("cat" in tags)

    def test_error_is_raised_when_no_tags_generated(self):
        image_name = "image4_should_error.jpg"
        image = open_image(image_name)

        with self.assertRaises(ValueError):
            detect(image)

    def test_detection_for_every_image(self):
        test_image_names = get_every_file_name_in_dir()
        # load images and perform detection
        for image_name in test_image_names:
            if image_name != "image4_should_error.jpg":
                image = open_image(image_name)
                self.assertIsNotNone(image, "Failed to load image")

                tags = detect(image)
                print('Detection Complete for {}:\ntags:{}\n'.format(image_name, pretty_print_tags(tags)))
                self.assertTrue(len(tags) >= 1)

    def test_results_page_shows_image(self):
        client = Client()
        with open(TEST_IMAGES_DIR + "/image1.jpg", "rb") as file, open(TEST_IMAGES_DIR + "/image2.jpg", "rb") as file2:
            response = client.post(reverse('classify'), { 'file' : [file, file2]})
        self.assertIsNotNone(response.context['results'])

    # this cleans up the test images after the tests in this class are run
    @classmethod
    def tearDownClass(cls):
        delete_test_images()


# Helper Functions
def open_image(image_name):
    try:
        image = Image.open(os.path.join(TEST_IMAGES_DIR, image_name))
        print("Successfully loaded image: {}".format(image_name))
        return image
    except IOError:
        print("Failed to load image: {}".format(image_name))


def pretty_print_tags(str_list):
    list_of_tags = ', '.join(map(str, str_list))
    return "[" + list_of_tags + "]"


def get_every_file_name_in_dir():
    test_image_names = [f for f in os.listdir(TEST_IMAGES_DIR) if os.path.isfile(os.path.join(TEST_IMAGES_DIR, f))]
    return test_image_names
