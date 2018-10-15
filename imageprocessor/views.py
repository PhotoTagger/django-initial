from django.shortcuts import render
from django.http import HttpResponse
from imageprocessor.forms import ImageForm
from PIL import Image
from imageprocessor.tagservice.tagger import detect


# Create your views here.
def index(request):
	return render(request, 'index.html')
def classify(request):
	context = {}
	if request.method =='POST':
		image = Image.open(request.FILES.get('file'))
		context['tags'] = detect(image)
		return render(request, 'output.html', context)
	form = ImageForm(request.POST or None)
	context['form'] = form
	return render(request, 'input.html', context)