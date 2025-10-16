from django.urls import path

from .user import get, update, delete, action

app_name = 'user'

urlpatterns = [
    path('get/', get, name='get'),
    path('update/', update, name='update'),
    path('delete/', delete, name='delete'),
    path('action/', action, name='action'),
]
