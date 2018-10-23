from builtins import OSError, ValueError

from django.shortcuts import render
from django.http import HttpResponse
from imageprocessor.forms import ImageForm
from PIL import Image
from imageprocessor.tagservice.tagger import detect


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
			context['errors'] = True
		except OSError:
			context['errors'] = True
	context['form'] = form
	return render(request, 'input.html', context)
