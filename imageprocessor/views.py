from django.shortcuts import render
from django.http import HttpResponse
from imageprocessor.forms import ImageForm

# Create your views here.
def index(request):
	context = {}
	if request.method =='POST':
		context['form'] = 'hey you uploaded an image'
		return render(request, 'index.html', context)
	form = ImageForm(request.POST or None)
	context['form'] = form
	return render(request, 'index.html', context)