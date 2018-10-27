from django import forms
from .models import UploadedImage

from cloudinary.forms import CloudinaryJsFileField, CloudinaryUnsignedJsFileField
# Next two lines are only used for generating the upload preset sample name
from cloudinary.compat import to_bytes
import cloudinary, hashlib

from .models import Photo


class ImageForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = UploadedImage
        fields = ['file']


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = '__all__'


class PhotoDirectForm(PhotoForm):
    image = CloudinaryJsFileField()


class PhotoUnsignedDirectForm(PhotoForm):
    upload_preset_name = "sample_" + hashlib.sha1(to_bytes(cloudinary.config().api_key + cloudinary.config().api_secret)).hexdigest()[0:10]
    image = CloudinaryUnsignedJsFileField(upload_preset_name)
