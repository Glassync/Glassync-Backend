from django.urls import path, include

from .profile import get, update, delete

urlpatterns = [
    path('get/', get),
    path('update/', update),
    path('delete/', delete),
]
