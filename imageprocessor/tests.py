from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from .tagservice.test import TEST_IMAGES_DIR
from PIL import Image

import os

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

class LoginTests(TestCase):
    def test_register_creates_new_user(self):
        original_user_count = User.objects.all().count()
        client = Client()
        response = client.post(reverse('register'),{'username': "TestUser1", 'password1': "testpassword1", 'password2': "testpassword1"})
        self.assertEqual(response.status_code,302)
        #checking that the count of users has increase by one from original
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
        self.assertEqual(response.status_code, 200)
        self.assertIn('cat', response.data)
        self.assertIn('dog', response.data)
