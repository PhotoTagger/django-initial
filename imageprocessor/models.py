from builtins import AttributeError

from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User


class Photo(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField("Title (optional)", max_length=200, blank=True)
    #file = CloudinaryField('file')
    url = models.CharField(max_length=250, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank = True)

    def create_related_tags(self, tags):
        for tag in tags:
            new_tag = Tag(photo=self, tag=tag)
            new_tag.save()
    def get_tags(self):
        return self.tag_set.all()
class Tag(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, null=True, blank=True)
    tag = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.tag
