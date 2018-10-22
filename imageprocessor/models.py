from django.db import models

class UploadedImage(models.Model):
    file = models.FileField(upload_to="images/")

