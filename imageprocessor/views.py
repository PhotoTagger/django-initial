from builtins import OSError, ValueError, len

from django.http import HttpResponseRedirect
from django.urls import reverse
import cloudinary
from django.contrib.auth.forms import UserCreationForm
from PIL import Image
from imageprocessor.tagservice.tagger import detect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import render
from .forms import ImageForm
from .models import Photo


NO_TAGS_ERROR_MSG = "We couldn't generate tags for that image. Please try a different photo"
BAD_FILE_ERROR_MSG = "We can't process that file type. Please submit a different file"


# Create your views here.
def index(request):
    return render(request, 'index.html')


def tag_search(request):
    context = {}
    if request.method == 'POST':
        search_query = request.POST["tagsearch"]
        search = 'resource_type:image AND tags=' + search_query

        result = cloudinary.Search() \
                .expression(search) \
                .with_field('tags') \
                .max_results('10') \
                .execute()

        images = []

        if result and 'resources' in result:
            for img in result["resources"]:
                images.append(img["url"])

        context['search_query'] = search_query
        context['images'] = images
        context['search_result'] = result

        return render(request, 'tagged_pictures.html', context)

    return render(request, 'tagsearch.html')


def tagged_pictures(request):
    return render(request, 'tagged_pictures.html')


def get_tags_for_single_image(request):
    tags = []
    try:
        open_image = Image.open(request.FILES.get('file'))
        tags = detect(open_image)

        # this line enables us to read from the file more than once
        request.FILES.get('file').seek(0)
    except ValueError:
        messages.add_message(request, messages.ERROR, NO_TAGS_ERROR_MSG)
    except OSError:
        messages.add_message(request, messages.ERROR, BAD_FILE_ERROR_MSG)
    return tags


def get_tags_for_image(request, img):
    tags = []
    try:
        open_image = Image.open(img)
        tags = detect(open_image)
        return tags
    except ValueError:
        messages.add_message(request, messages.ERROR, NO_TAGS_ERROR_MSG)
    except OSError:
        messages.add_message(request, messages.ERROR, BAD_FILE_ERROR_MSG)
    return tags


def upload_image_to_cloudinary(file, tags):
    file.seek(0)

    return cloudinary.uploader.upload(
        file,
        use_filename=True,
        tags=tags
    )


def process_bulk_images(request):
    files = request.FILES.getlist('file')
    results = []
    for img in files:
        res = {}
        current_tag = get_tags_for_image(request, img)
        current_res = upload_image_to_cloudinary(img, current_tag)

        res['tags'] = current_tag
        res['url'] = current_res.get('url', '')
        results.append(res)
    return results


def process_single_image(request):
    data = {}
    generated_tags = get_tags_for_single_image(request)
    response_data = upload_image_to_cloudinary(request.FILES.get('file'), generated_tags)

    data['tags'] = generated_tags or None
    data['url'] = response_data.get('url', '') or None

    return [data]



def classify(request):
    context = {'form': ImageForm()}

    if request.method == 'POST':
        image_count = len(request.FILES.getlist('file'))
        context['results'] = process_single_image(request) if image_count <= 1 else process_bulk_images(request)

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
        response_data = {
            'url' : None,
            'tags' : []
        }      
        try:
            image_file = request.FILES['file']
            image = Image.open(image_file)
            tags = detect(image) 
            if (tags):
                try:
                    response_data['tags'] = tags
                    current_res = upload_image_to_cloudinary(image_file, tags)
                    response_data['url'] = current_res.get('url', '') or None
                    return Response(response_data, status=status.HTTP_200_OK)
                except:
                    return Response(response_data, status=status.HTTP_202_ACCEPTED)
            return Response(NO_TAGS_ERROR_MSG, status=status.HTTP_204_NO_CONTENT)
        except ValueError:
            return Response(NO_TAGS_ERROR_MSG, status=status.HTTP_204_NO_CONTENT)
        except OSError:
            return Response(BAD_FILE_ERROR_MSG, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
