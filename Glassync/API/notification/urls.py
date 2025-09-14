from django.urls import path, include

from .notification import get

app_name = 'notification'

urlpatterns = [
    path('get/', get, name='get'),
    path('platform/', include('Glassync.API.notification.platform.urls', namespace='platform')),
]
