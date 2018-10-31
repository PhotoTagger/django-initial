from builtins import OSError, ValueError

from django.shortcuts import render
from imageprocessor.models import UploadedImage
from imageprocessor.forms import ImageForm
from PIL import Image
from imageprocessor.tagservice.tagger import detect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

NO_TAGS_ERROR_MSG = "We couldn't generate tags for that image. Please try a different photo"
BAD_FILE_ERROR_MSG = "We can't process that file type. Please submit a different file"


# Create your views here.
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

