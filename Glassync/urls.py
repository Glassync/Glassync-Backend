from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.event_list, name='event_list'),  # Event list page
    path('events/create/', views.create_event, name='create_event'),  # Event creation page
    path('events/edit/<int:event_id>/', views.edit_event, name='edit_event'),  # Event editing page
    path('events/delete/<int:event_id>/', views.delete_event, name='delete_event'),  # Event deletion page
    path('events/filter/', views.filter_events, name='filter_events'),  # Filtering events page
]
