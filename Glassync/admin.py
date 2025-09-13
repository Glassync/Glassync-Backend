from django.contrib import admin
from .models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'day', 'start_time', 'end_time', 'recurrence_rule')


admin.site.register(Event, EventAdmin)
