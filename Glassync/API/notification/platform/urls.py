from django.urls import path, include

from .platform import get, update

app_name = 'platform'

urlpatterns = [
    path('get/', get, name='get'),
    path('update/', update, name='update'),
]
