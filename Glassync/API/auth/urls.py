from django.urls import path, include

from .auth import login, signup, logout

app_name = 'auth'

urlpatterns = [
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),
    path('platform/', include('Glassync.API.auth.platform.urls', namespace='auth'))
]