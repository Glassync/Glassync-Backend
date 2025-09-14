from django.urls import path, include

from .user import get, action

urlpatterns = [
    path('get/', get),
    path('action/', action),
    path('profile/', include('Glassync.API.user.profile.urls')),
]
