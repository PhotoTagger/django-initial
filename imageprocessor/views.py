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
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

NO_TAGS_ERROR_MSG = "We couldn't generate tags for that image. Please try a different photo"
BAD_FILE_ERROR_MSG = "We can't process that file type. Please submit a different file"


# Create your views here.
def index(request):
    return render(request, 'index.html')


def tag_search(request):
    context = {}
    if request.method == 'POST':
        context['tag'] = request.POST["tagsearch"]
        return render(request, 'tagged_pictures.html', context)
        # whatever is typed in, will be stored into tag_searched
        # tag_searched = request.POST["tag"]
        # context['tag'] = tag_searched
    return render(request, 'tagsearch.html')



def tagged_pictures(request):
    return render(request, 'tagged_pictures.html')

def generate_tags(request):
    tags = []
    for image_file in request.FILES.getlist('file'):
        image = Image.open(image_file)
        tags_found = detect(image)
        tags.append(tags_found)
    return tags

def format_tags(tags):
    tag_string_list = []
    pic_number = 1
    for tags_found in tags:
        tag_string = ', '.join(map(str, tags_found))
        tag_string_list.append(f'{pic_number}: {tag_string}.')
        pic_number += 1

    return tag_string_list

def save_image(request):
    ''' '''
    form = ImageForm(request.POST or None, request.FILES or None)
    new_image_list = []
    # this try except was added so application works while the database is not working.
    try:
        if form.is_valid():
            for image_file in request.FILES.getlist('file'):
                instance = UploadedImage(file = image_file)
                instance.save()
                new_image_list.append(instance)
        '''if form.is_valid():
            new_image = form.save()
            new_image.save()
            return new_image'''
        return new_image_list
    except:
        messages.add_message(request, messages.ERROR, "image not saved")


@csrf_exempt
def classify(request):
    form = ImageForm(request.POST or None, request.FILES or None)
    context = {"form": form}
    if request.method == 'POST':
        try:
            tags = generate_tags(request)
            context['tags'] = format_tags(tags)
            context['new_image'] = save_image(request)
            # print(type(context['new image']))
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

class ClassifyAPI(APIView):

    def post(self, request, format=None):           
        try:
            image_file = request.FILES['file']
            image = Image.open(image_file)
            tags = detect(image)
            #this try except was added so application works while the database is not working.
            try:
                new_image = form.save()
                new_image.save()
                context['new_image'] = new_image
            except:
                return Response(tags, status=status.HTTP_202_ACCEPTED)
            return Response(tags, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(NO_TAGS_ERROR_MSG, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except OSError as e:
            return Response(BAD_FILE_ERROR_MSG, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
