from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

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
        print(response.content)
        self.assertTrue(response.status_code == 200)

    def tag_search_test(self):
        client = Client()
        response = client.get("/tagsearch/")
        self.assertTrue(response.status_code == 200)

    def tag_search__tagged_pictures_test(self):
        client = Client()
        response = client.get("/tagsearch/tagged_pictures/")
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


