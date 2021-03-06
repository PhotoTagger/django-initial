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
from imageprocessor.views import classify, index, tag_search, tagged_pictures, register, ClassifyAPI, view_my_pictures
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = [
    path('registration/', include('django.contrib.auth.urls')),
    path('register/', register, name='register'),
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('tagsearch/', tag_search, name = 'tagsearch'),
    path('viewmypictures/', view_my_pictures, name = 'view_my_pictures'),
    path('tagsearch/tagged_pictures/', tagged_pictures, name = 'tagsearch/tagged_pictures'),
    path('classify/', classify, name='classify'),
    path('api/classify/', ClassifyAPI.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
