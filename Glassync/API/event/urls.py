from django.urls import path

from .event import get, create, update, delete, action

app_name = 'event'

urlpatterns = [
    path('get/', get, name='get'),
    path('create/', create, name='create'),
    path('update/', update, name='update'),
    path('delete/', delete, name='delete'),
    path('action/', action, name='action'),
]
