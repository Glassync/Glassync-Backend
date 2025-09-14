from django.urls import path, include

from .platform import get, update

urlpatterns = [
    path('get/', get),
    path('update/', update),
]
