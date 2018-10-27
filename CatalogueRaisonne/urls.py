"""CatalogueRaisonne URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from imageprocessor.views import classify, index, tag_search, tagged_pictures, register, list, upload, direct_upload_complete
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import urls


admin.autodiscover()

urlpatterns = [

    path('list/', list),
    path('list2', list, name='photo_album.views.list'),
    # URL for uploading an image
    path('upload/', upload, name='photo_album.views.upload'),
    # The direct upload functionality reports to this URL when an image is uploaded.
    path('upload/complete/', direct_upload_complete, name='photo_album.views.direct_upload_complete'),

    path('registration/', include('django.contrib.auth.urls')),
    path('register/', register, name='register'),
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('tagsearch/', tag_search, name = 'tagsearch'),
    path('tagsearch/tagged_pictures/', tagged_pictures, name = 'tagsearch/tagged_pictures'),
    path('classify/', classify, name='classify')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
