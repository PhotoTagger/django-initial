from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

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

    def test_results_page_shows_image(self):
        client = Client()
        with open(TEST_IMAGES_DIR + "/image1.jpg", "rb") as file:
            response = client.post(reverse('classify'), {'file': file})
        self.assertIsNotNone(response.context['results'][0]['url'])
        self.assertTrue('dog' in response.context['results'][0]['tags'])

    def test_results_page_shows_image_should_error(self):
        client = Client()
        with open(TEST_IMAGES_DIR + "/image4_should_error.jpg", "rb") as blankImageFile:
            response = client.post(reverse('classify'), {'file': blankImageFile})
        self.assertIsNotNone(response.context['results'][0]['url'])
        self.assertIsNone(response.context['results'][0]['tags'])

    def test_results_page_shows_images(self):
        client = Client()
        with open(TEST_IMAGES_DIR + "/image1.jpg", "rb") as file1, open(TEST_IMAGES_DIR + "/image4_should_error.jpg", "rb") as file2:
            response = client.post(reverse('classify'), {'file': [file1, file2]})
        self.assertIsNotNone(response.context['results'][0]['url'])
        self.assertIsNotNone(response.context['results'][1]['url'])
        self.assertTrue('dog' in response.context['results'][0]['tags'])
        self.assertTrue(response.context['results'][1]['tags'] == [])

    def test_tag_search_post_request_works(self):
        client = Client()
        response = client.post("/tagsearch/", {'tagsearch': ['dog']})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.context['search_result'].get("total_count") >= 1)


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

