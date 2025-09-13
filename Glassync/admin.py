from django.contrib import admin
from .models import Event, RecurringEvent


class RecurringEventInline(admin.StackedInline):
    model = RecurringEvent
    extra = 1  # Show one extra form in the admin for adding a recurring event


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'user')
    search_fields = ('title', 'description')
    inlines = [RecurringEventInline]  # Add RecurringEvent inline in Event Admin


admin.site.register(Event, EventAdmin)
