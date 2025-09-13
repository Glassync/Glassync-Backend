from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.urls import reverse_lazy

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect(reverse_lazy('event_list'))),
    path('accounts/', include('accounts.urls')),
    path('events/', include('Glassync.urls')),
]
