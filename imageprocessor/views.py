from builtins import OSError, ValueError

from django.shortcuts import render
from base64 import b64encode
# from .models import UploadedImage
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
import cloudinary
from django.contrib.auth.forms import UserCreationForm
# from imageprocessor.forms import ImageForm
from PIL import Image
from imageprocessor.tagservice.tagger import detect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

import json

import six
from cloudinary import api  # Only required for creating upload presets on the fly
# from cloudinary.forms import cl_init_js_callbacks
from django.http import HttpResponse
from django.shortcuts import render

from .forms import PhotoForm, PhotoUnsignedDirectForm
from .models import Photo

NO_TAGS_ERROR_MSG = "We couldn't generate tags for that image. Please try a different photo"
BAD_FILE_ERROR_MSG = "We can't process that file type. Please submit a different file"
DEFAULT_TAG = "python_sample_basic"


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


# def save_image(request):
    # form = ImageForm(request.POST or None, request.FILES or None)
    # this try except was added so application works while the database is not working.
    # try:
    #     if form.is_valid():
    #         new_image = form.save()
    #         new_image.save()
    #         return new_image
    # except:
    #     messages.add_message(request, messages.ERROR, "image not saved")

@csrf_exempt
def classify(request):
    # form = ImageForm(request.POST or None, request.FILES or None)
    # context = {"form": form}
    context = {}
    if request.method == 'POST':
        try:
            context['tags'] = get_tags_for_images(request)
            # context['new_image'] = save_image(request)
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


@csrf_exempt
def upload(request):
    # try:
    #     api.upload_preset(PhotoUnsignedDirectForm.upload_preset_name)
    # except api.NotFound:
    #     print("api upload preset didn't work")
    #     api.create_upload_preset(name=PhotoUnsignedDirectForm.upload_preset_name, unsigned=True, folder="preset_folder")

    context = dict(
        # Form demonstrating backend upload
        backend_form=PhotoForm(),
        # Should the upload form be unsigned
        unsigned=False,
    )

    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        posted = form.instance
        context['posted'] = posted

        # if form.is_valid():
        #     form.save()

        thing = request.FILES.get('image')
        Image.open(thing)
        print(thing)

        res = cloudinary.uploader.upload(
            request.FILES.get('image'),
            public_id='sample_id',
            crop='limit',
            width=2000,
            height=2000,
            eager=[
                {'width': 200, 'height': 200,
                 'crop': 'thumb', 'gravity': 'face',
                 'radius': 20, 'effect': 'sepia'},
                {'width': 100, 'height': 150,
                 'crop': 'fit', 'format': 'png'}
            ],
            tags=['special', 'for_homepage']
        )

        print(res)
        # context['res'] = res

        # print(res.get('url'))
        context['url'] = res.get('url', 'not available')

        # opening the image has to happen after the form is saved
        img = request.FILES.get('image')
        # image = Image.open(img)
        context['tags'] = detect(img)
        print(context['tags'])

    return render(request, 'upload.html', context)


def filter_nones(d):
    return dict((k, v) for k, v in six.iteritems(d) if v is not None)


def list(request):
    defaults = dict(format="jpg", height=150, width=150)
    defaults["class"] = "thumbnail inline"

    # The different transformations to present
    samples = [
        dict(crop="thumb", gravity="face"),
        dict(format="png", angle=20, height=None, width=None, transformation=[
            dict(crop="fill", gravity="north", width=150, height=150, effect="sepia"),
        ]),
    ]
    samples = [filter_nones(dict(defaults, **sample)) for sample in samples]
    return render(request, 'list.html', dict(photos=Photo.objects.all(), samples=samples))

