from builtins import AttributeError

from django.db import models
from cloudinary.models import CloudinaryField


class Photo(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField("Title (optional)", max_length=200, blank=True)
    file = CloudinaryField('file')

    def __unicode__(self):
        try:
            public_id = self.file.public_id
        except AttributeError:
            public_id = ''
        return "Photo <%s:%s>" % (self.title, public_id)
