from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('create/', views.create_event, name='create_event'),
    path('edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('filter/', views.filter_events, name='filter_events'),
    path('', views.event_list, name='event_list'),
]
