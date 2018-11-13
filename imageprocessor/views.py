from builtins import OSError, ValueError, len

from django.http import HttpResponseRedirect
from django.urls import reverse
import cloudinary
from django.contrib.auth.forms import UserCreationForm
from PIL import Image
from imageprocessor.tagservice.tagger import detect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import render
from django.conf import settings
from .forms import ImageForm
from .models import Photo, Tag


NO_TAGS_ERROR_MSG = "We couldn't generate tags for that image. Please try a different photo"
BAD_FILE_ERROR_MSG = "We can't process that file type. Please submit a different file"
CLOUDINARY_ERROR = "We were able to generate tags for the image, but an error occured while attempting to save the image on our end"


# Create your views here.
def index(request):
    return render(request, 'index.html')


def tag_search(request):
    context = {}
    if request.method == 'POST':
        search_query = request.POST["tagsearch"]

        result = cloudinary.Search() \
                .expression(f'tags={search_query}') \
                .with_field('tags') \
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
    
    result = cloudinary.uploader.upload(
        file,
        tags=tags,
        folder=settings.UPLOAD_FOLDER)

    #etag is unique identifier for picture
    etag = result.get('etag', None)

    try:
        # if it is the first time we uploaded image onto database, then we will rename public_ic with etag
        result = cloudinary.uploader.rename(result.get('public_id'), etag)
        # if there's no duplicate images, its safe to return the original image data
        return result
    except:
        # Exception will occur when trying to rename more than one photo
        # Thus we will delete the uploaded image in the database
        cloudinary.api.delete_resources([result.get('public_id', None)])

        # We need to find the original photo, not the photo that was originally posted
        # This is because photo originally posted was deleted
        original_photo = cloudinary.Search() \
            .expression(f'public_id={etag}') \
            .execute()

        result['url'] = original_photo["resources"][0]['url']
        result['public_id'] = original_photo["resources"][0]['public_id']
        return result

def process_bulk_images(request):
    files = request.FILES.getlist('file')
    results = []
    for img in files:
        res = {}
        current_tag = get_tags_for_image(request, img)
        current_res = upload_image_to_cloudinary(img, current_tag)

        res['tags'] = current_tag
        res['url'] = current_res.get('url', None)
        res['public_id'] = current_res.get('public_id', None)
        results.append(res)
    return results


def process_single_image(request):
    data = {}
    generated_tags = get_tags_for_single_image(request)
    response_data = upload_image_to_cloudinary(request.FILES.get('file'), generated_tags)

    data['tags'] = generated_tags or None
    data['url'] = response_data.get('url', None)
    data['public_id'] = response_data.get('public_id', None)

    return [data]


def classify(request):
    form = ImageForm(request.POST or None, request.FILES or None)
    context = {'form' :form }
    if request.method == 'POST':
        image_count = len(request.FILES.getlist('file'))
        context['results'] = process_single_image(request) if image_count <= 1 else process_bulk_images(request)
        if request.user.is_authenticated:
            for result in context['results']:
                new_photo = Photo(url = result['url'], user = request.user, title = request.POST.get("title", "") )
                new_photo.save()
                new_photo.create_related_tags(result['tags'])
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

@login_required(login_url='/registration/login/')
def view_my_pictures(request):
    context = {'my_pictures' : Photo.objects.filter(user = request.user)}
    return render(request, 'view_my_pictures.html', context)

class ClassifyAPI(APIView):

    def post(self, request, format=None):
        response_data = { 'results': None }    
        results = []
        
        image_files = request.FILES.getlist('file')
        if len(image_files) < 1:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            for image_file in image_files:
                result = {
                    'status': None,
                    'error_message': None,
                    'name': image_file.name,
                    'public_id': None,
                    'url' : None,
                    'tags' : []
                }
                try:
                    image = Image.open(image_file)
                    tags = detect(image)
                    result['tags'] = tags
                    try:
                        current_res = upload_image_to_cloudinary(image_file, tags)
                        result['url'] = current_res.get('url', None)
                        result['public_id'] = current_res.get('public_id', None)
                        result['status'] = status.HTTP_200_OK
                    except:
                        result['status'] = status.HTTP_202_ACCEPTED
                        result['error_message'] = CLOUDINARY_ERROR
                except ValueError:
                    result['status'] = status.HTTP_204_NO_CONTENT
                    result['error_message'] = NO_TAGS_ERROR_MSG
                except OSError:
                    result['status'] = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
                    result['error_message'] = BAD_FILE_ERROR_MSG
                except:
                    result['status'] = status.HTTP_400_BAD_REQUEST
                
                results.append(result)
            
            response_data['results'] = results
            return Response(data=response_data, status=status.HTTP_207_MULTI_STATUS)
