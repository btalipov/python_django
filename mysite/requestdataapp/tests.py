import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .views import MAX_UPLOAD_SIZE

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FileUploadTestCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_small_file_is_saved(self):
        myfile = SimpleUploadedFile("small.txt", b"x" * MAX_UPLOAD_SIZE)
        response = self.client.post(reverse("requestdataapp:file-upload"), {"myfile": myfile})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Saved file: small.txt")

    def test_large_file_is_rejected(self):
        myfile = SimpleUploadedFile("large.txt", b"x" * (MAX_UPLOAD_SIZE + 1))
        response = self.client.post(reverse("requestdataapp:file-upload"), {"myfile": myfile})
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "too large", status_code=400)


@override_settings(THROTTLING_INTERVAL=60)
class ThrottlingMiddlewareTestCase(TestCase):
    def test_frequent_requests_are_throttled(self):
        client = Client()
        url = reverse("shopapp:index")
        self.assertEqual(client.get(url).status_code, 200)
        response = client.get(url)
        self.assertEqual(response.status_code, 429)
        self.assertContains(response, "Too many requests", status_code=429)

    def test_different_ip_is_not_throttled(self):
        client = Client()
        url = reverse("shopapp:index")
        self.assertEqual(client.get(url, REMOTE_ADDR="10.0.0.1").status_code, 200)
        self.assertEqual(client.get(url, REMOTE_ADDR="10.0.0.2").status_code, 200)
