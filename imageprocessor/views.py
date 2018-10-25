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


@csrf_exempt
def classify(request):
	context = {}
	form = ImageForm(request.POST or None, request.FILES or None)
	if request.method == 'POST':
		try:
			image_file = request.FILES['file']
			image = Image.open(image_file)
			context['tags'] = detect(image)
			new_image = form.save()
			new_image.save()
			context['new_image'] = new_image
			return render(request, 'output.html', context)
		except ValueError:
			messages.add_message(request, messages.ERROR, NO_TAGS_ERROR_MSG)
		except OSError:
			messages.add_message(request, messages.ERROR, BAD_FILE_ERROR_MSG)
	context['form'] = form
	return render(request, 'input.html', context)

def register(request):
	context = {}
	form = UserCreationForm(request.POST or None)
	if request.method == 'POST':
		new_user = form.save()
		new_user.save()
		return HttpResponseRedirect(reverse('login'))
	context['form'] = form
	return render(request, 'register.html', context)

