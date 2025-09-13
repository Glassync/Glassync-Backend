from django.db import models
from django.contrib.auth.models import User


# Event Model
class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.start_time}"


# Recurring Event Model
class RecurringEvent(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    recurrence_type = models.CharField(max_length=20)  # daily, weekly, etc.
    interval = models.IntegerField(default=1)  # Repeat every X days, weeks, etc.
    days_of_week = models.CharField(max_length=255, blank=True)  # e.g., 'Monday, Wednesday'
    month_day = models.IntegerField(blank=True, null=True)  # e.g., "15th"
    end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Recurring: {self.event.title}"

