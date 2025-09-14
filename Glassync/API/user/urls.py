from django.urls import path, include

from .user import get, action

app_name = 'user'

urlpatterns = [
    path('get/', get, name='get'),
    path('action/', action, name='action'),
    path('profile/', include('Glassync.API.user.profile.urls', namespace='profile')),
]
