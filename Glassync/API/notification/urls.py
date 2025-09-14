from django.urls import path, include

from .notification import get

urlpatterns = [
    path('get/', get),
    path('platform/', include('Glassync.API.notification.platform.urls')),
]
