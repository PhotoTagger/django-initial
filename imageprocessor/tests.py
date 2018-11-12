from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from .views import NO_TAGS_ERROR_MSG, BAD_FILE_ERROR_MSG, CLOUDINARY_ERROR

import cloudinary
from PIL import Image

import cloudinary

import os
import io

TEST_IMAGES_DIR = 'imageprocessor/tagservice/test_images'


# Create your tests here.
class ViewTests(TestCase):
    def test_view_initialized_successfully(self):
        self.assertTrue(True)

    def test_index_view(self):
        client = Client()
        response = client.get("/")
        self.assertTrue(response.status_code == 200)

    def test_classify_view(self):
        client = Client()
        response = client.get("/classify/")
        self.assertTrue(response.status_code == 200)

    def test_tag_search(self):
        client = Client()
        response = client.get("/tagsearch/")
        self.assertTrue(response.status_code == 200)

    def test_tag_search__tagged_pictures(self):
        client = Client()
        response = client.get("/tagsearch/tagged_pictures/")
        self.assertTrue(response.status_code == 200)

    def test_register_page(self):
        client = Client()
        response = client.get(reverse('register'))
        self.assertTrue(response.status_code == 200)

    def test_not_logged_in_user_cannot_view_my_pictures(self):
        client = Client()
        response = client.get(reverse('view_my_pictures'))
        self.assertTrue(response.status_code == 302)

    def test_logged_in_user_can_view_my_pictures(self):
        client = Client()
        client.post(reverse('register'),{'username': "TestUser1", 'password1': "testpassword1", 'password2': "testpassword1"})
        client.login(username="TestUser1", password="testpassword1")
        response = client.get(reverse('view_my_pictures'))
        self.assertTrue(response.status_code == 200)

    def test_view_my_pictures_picture_count(self):
        client = Client()
        response = client.post(reverse('register'),{'username': "TestUser1", 'password1': "testpassword1", 'password2': "testpassword1"})
        client.login(username="TestUser1", password="testpassword1")
        images_to_upload = 5
        for i in range(images_to_upload):
            with open(TEST_IMAGES_DIR + "/image1.jpg", "rb") as file:
                    client.post(reverse('classify'), {'file': file})
        response = client.get(reverse('view_my_pictures'))
        self.assertEqual(len(response.context['my_pictures']) ,images_to_upload)
        for picture in response.context['my_pictures']:
            self.assertTrue('dog' in picture.get_tags().values_list('tag', flat=True))

    def test_results_page_shows_image(self):
        client = Client()
        with open(TEST_IMAGES_DIR + "/image1.jpg", "rb") as file:
            response = client.post(reverse('classify'), {'file': file})
        self.assertIsNotNone(response.context['results'][0]['url'])
        self.assertTrue('dog' in response.context['results'][0]['tags'])
        cloudinary.uploader.destroy(response.context['results'][0]['public_id'], invalidate=True)

    def test_results_page_shows_image_should_error(self):
        client = Client()
        with open(TEST_IMAGES_DIR + "/image4_should_error.jpg", "rb") as blankImageFile:
            response = client.post(reverse('classify'), {'file': blankImageFile})
        self.assertIsNotNone(response.context['results'][0]['url'])
        self.assertIsNone(response.context['results'][0]['tags'])
        cloudinary.uploader.destroy(response.context['results'][0]['public_id'], invalidate=True)

    def test_results_page_shows_images(self):
        client = Client()
        with open(TEST_IMAGES_DIR + "/image1.jpg", "rb") as file1, open(TEST_IMAGES_DIR + "/image4_should_error.jpg", "rb") as file2:
            response = client.post(reverse('classify'), {'file': [file1, file2]})
        self.assertIsNotNone(response.context['results'][0]['url'])
        self.assertIsNotNone(response.context['results'][1]['url'])
        self.assertTrue('dog' in response.context['results'][0]['tags'])
        self.assertTrue(response.context['results'][1]['tags'] == [])
        cloudinary.uploader.destroy(response.context['results'][0]['public_id'], invalidate=True)
        cloudinary.uploader.destroy(response.context['results'][1]['public_id'], invalidate=True)


    def test_tag_search_post_request_works(self):
        client = Client()
        response = client.post("/tagsearch/", {'tagsearch': ['dog']})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.context['search_result'].get("total_count") >= 1)

    def test_post_same_image_with_different_name(self):
        client = Client()
        with open(TEST_IMAGES_DIR + "/image5.jpg", "rb") as file1, open(TEST_IMAGES_DIR + "/same_as_image5.jpg", "rb") as file2:
            response = client.post(reverse('classify'), {'file': [file1, file2]})
        query = 'resource_type:image AND public_id=fce00b1df488c389916f9994a23fca10'
        search_query_result = cloudinary.Search().expression(query).execute()
        self.assertEqual(search_query_result["total_count"], 1)
        cloudinary.api.delete_resources(['fce00b1df488c389916f9994a23fca10'])

    #this cleans up the test images after the tests in this class are run
    @classmethod
    def tearDownClass(cls):
        delete_test_images()

class LoginTests(TestCase):
    def test_register_creates_new_user(self):
        original_user_count = User.objects.all().count()
        client = Client()
        response = client.post(reverse('register'),{'username': "TestUser1", 'password1': "testpassword1", 'password2': "testpassword1"})
        self.assertEqual(response.status_code,302)
        # checking that the count of users has increase by one from original
        self.assertEqual(original_user_count + 1, User.objects.all().count())

    def test_new_user_able_to_login(self):
        client = Client()
        response = client.post(reverse('register'),{'username': "TestUser1", 'password1': "testpassword1", 'password2': "testpassword1"})
        self.assertTrue(client.login(username="TestUser1", password="testpassword1"))

class ClassifyApiTests(APITestCase):

    def test_classify_api_no_image(self):
        response = self.client.post("/api/classify/")
        self.assertEqual(response.status_code, 400)

    def test_classify_api_cat_and_dog(self):
        with open(os.path.join(TEST_IMAGES_DIR,"image3.jpg"), "rb") as file:
            response = self.client.post("/api/classify/", {'file': file}, format='multipart')   
        self.assertEqual(response.status_code, 207)
        result = response.data['results'][0]
        self.assertEqual(result['status'], 200)
        self.assertIsNone(result['error_message'])
        self.assertEqual(result['name'], 'image3.jpg')
        self.assertIsNotNone(result['url'])
        self.assertIsNotNone(result['public_id'])
        self.assertIn('cat', result['tags'])
        self.assertIn('dog', result['tags'])
        cloudinary.uploader.destroy(result['public_id'], invalidate=True)

    def test_classify_api_muliple_images(self):
        with open(os.path.join(TEST_IMAGES_DIR,"image3.jpg"), "rb") as file1, open(os.path.join(TEST_IMAGES_DIR,"image2.jpg"), "rb") as file2:
            response = self.client.post("/api/classify/", {'file': [file1, file2]}, format='multipart')
        self.assertEqual(response.status_code, 207)
        
        result = response.data['results'][0]
        self.assertEqual(result['status'], 200)
        self.assertIsNone(result['error_message'])
        self.assertEqual(result['name'], 'image3.jpg')
        self.assertIsNotNone(result['url'])
        self.assertIsNotNone(result['public_id'])
        self.assertIn('cat', result['tags'])
        self.assertIn('dog', result['tags'])
        cloudinary.uploader.destroy(result['public_id'], invalidate=True)

        result = response.data['results'][1]
        self.assertEqual(result['status'], 200)
        self.assertIsNone(result['error_message'])
        self.assertEqual(result['name'], 'image2.jpg')
        self.assertIsNotNone(result['url'])
        self.assertIsNotNone(result['public_id'])
        self.assertIn('kite', result['tags'])
        self.assertIn('person', result['tags'])
        cloudinary.uploader.destroy(result['public_id'], invalidate=True)

    def test_classify_api_no_content(self):
        with open(os.path.join(TEST_IMAGES_DIR,"image4_should_error.jpg"), "rb") as file:
            response = self.client.post("/api/classify/", {'file': file}, format='multipart')
        self.assertEqual(response.status_code, 207)
        result = response.data['results'][0]
        self.assertEqual(result['status'], 204)
        self.assertEqual(result['error_message'], NO_TAGS_ERROR_MSG)
        self.assertEqual(result['name'], 'image4_should_error.jpg')
        self.assertIsNone(result['public_id'])
        self.assertIsNone(result['url'])
        self.assertFalse(result['tags'])

    def test_classify_api_unsupported_media(self):
        with io.StringIO("This is not a file") as file:
            response = self.client.post("/api/classify/", {'file': file}, format='multipart')
        self.assertEqual(response.status_code, 207)
        result = response.data['results'][0]
        self.assertEqual(result['status'], 415)
        self.assertEqual(result['error_message'], BAD_FILE_ERROR_MSG)
        self.assertEqual(result['name'], 'file')
        self.assertIsNone(result['public_id'])
        self.assertIsNone(result['url'])
        self.assertFalse(result['tags'])

    #this cleans up the test images after the tests in this class are run
    @classmethod
    def tearDownClass(cls):
        delete_test_images()

#helper function
def delete_test_images():
    cloudinary.api.delete_resources_by_prefix('TEST_IMAGES/')