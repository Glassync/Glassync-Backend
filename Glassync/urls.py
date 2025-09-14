from django.urls import path, include

urlpatterns = [
    path('event/', include('Glassync.API.event.urls')),
    path('notification/', include('Glassync.API.notification.urls')),
    path('user/', include('Glassync.API.user.urls')),
]
