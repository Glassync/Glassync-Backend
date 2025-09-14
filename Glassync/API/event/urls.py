from django.urls import path

from .event import get, create, update, delete, action

urlpatterns = [
    path('get/', get),
    path('create/', create),
    path('update/', update),
    path('delete/', delete),
    path('action/', action),
]
