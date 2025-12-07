from django.urls import path

from Glassync.API.auth.platform.auth_telegram import handle_telegram_auth_result

app_name = 'auth'

urlpatterns = [
    path('init/', handle_telegram_auth_result, name='get_data_from_platform'),
]