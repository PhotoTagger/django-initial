from builtins import OSError, ValueError

from django.shortcuts import render
from django.http import HttpResponse
from imageprocessor.forms import ImageForm
from PIL import Image
from imageprocessor.tagservice.tagger import detect
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


def classify(request):
	context = {}
	form = ImageForm(request.POST or None)
	if request.method == 'POST':
		try:
			image_file = request.FILES.get('file')
			image = Image.open(image_file)
			context['tags'] = detect(image)
			return render(request, 'output.html', context)
		except ValueError:
			messages.add_message(request, messages.ERROR, NO_TAGS_ERROR_MSG)
			context['errors'] = True
		except OSError:
			messages.add_message(request, messages.ERROR, BAD_FILE_ERROR_MSG)
			context['errors'] = True
	context['form'] = form
	return render(request, 'input.html', context)
