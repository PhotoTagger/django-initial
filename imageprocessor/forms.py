from django import forms
from .models import UploadedImage


class ImageForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = UploadedImage
        fields = ['file']