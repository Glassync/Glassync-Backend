from django.urls import path, include

from .profile import get, update, delete

app_name = 'profile'

urlpatterns = [
    path('get/', get, name='get'),
    path('update/', update, name='update'),
    path('delete/', delete, name='delete'),
]
