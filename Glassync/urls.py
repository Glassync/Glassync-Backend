from django.urls import path, include

urlpatterns = [
    path('event/', include('Glassync.API.event.urls')),
]
