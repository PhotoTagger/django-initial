from builtins import OSError, ValueError

from django.shortcuts import render
from base64 import b64encode
from .models import UploadedImage
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from imageprocessor.forms import ImageForm
from PIL import Image
from imageprocessor.tagservice.tagger import detect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

NO_TAGS_ERROR_MSG = "We couldn't generate tags for that image. Please try a different photo"
BAD_FILE_ERROR_MSG = "We can't process that file type. Please submit a different file"


# Create your views here.
def index(request):
    return render(request, 'index.html')


def tag_search(request):
    return render(request, 'tagsearch.html')


def tagged_pictures(request):
    return render(request, 'tagged_pictures.html')


def get_tags_for_images(request):
    tags = []
    files = request.FILES.getlist('file')
    for img in files:
        image_name = img.name
        image = Image.open(img)
        tags.append({image_name: detect(image)})
    return tags


def save_image(request):
    form = ImageForm(request.POST or None, request.FILES or None)
    # this try except was added so application works while the database is not working.
    try:
        if form.is_valid():
            new_image = form.save()
            new_image.save()
            return new_image
    except:
        messages.add_message(request, messages.ERROR, "image not saved")

@csrf_exempt
def classify(request):
    form = ImageForm(request.POST or None, request.FILES or None)
    context = {"form": form}
    if request.method == 'POST':
        try:
            context['tags'] = get_tags_for_images(request)
            context['new_image'] = save_image(request)
        except ValueError:
            messages.add_message(request, messages.ERROR, NO_TAGS_ERROR_MSG)
            return render(request, 'input.html', context)
        except OSError:
            messages.add_message(request, messages.ERROR, BAD_FILE_ERROR_MSG)
            return render(request, 'input.html', context)
        return render(request, 'output.html', context)
    return render(request, 'input.html', context)


def register(request):
    context = {}
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST':
        try:
            new_user = form.save()
            new_user.save()
        except:
            messages.add_message(request, messages.ERROR, "user not added ")
        return HttpResponseRedirect(reverse('login'))
    context['form'] = form
    return render(request, 'register.html', context)

