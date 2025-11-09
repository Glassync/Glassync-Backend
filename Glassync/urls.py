from django.urls import path, include

urlpatterns = [
    path('event/', include('Glassync.API.event.urls', namespace='event')),
    path('notification/', include('Glassync.API.notification.urls', namespace='notification')),
    path('user/', include('Glassync.API.user.urls', namespace='user')),
    path('auth/', include('Glassync.API.auth.urls', namespace='auth')),
]
