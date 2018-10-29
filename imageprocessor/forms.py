from django import forms
from .models import UploadedImage

class ImageForm(forms.ModelForm):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = UploadedImage
        fields = ['file']