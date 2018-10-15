from django.test import TestCase, Client


# Create your tests here.
class ViewTests(TestCase):
    def test_view_initialized_successfully(self):
        self.assertTrue(True)

    def test_index_view(self):
        print("running view tests")
        client = Client()
        response = client.get("/")
        self.assertTrue(response.status_code == 200)

    def test_classify_view(self):
        print("running test for classify view")
        client = Client()
        response = client.get("/classify/")
        print(response.content)
        self.assertTrue(response.status_code == 200)
