from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import CustomUser


class RecurrenceRule(models.Model):
    class RecurrenceType(models.TextChoices):
        DAYS = 'DAYS', 'Days'
        WEEKS = 'WEEKS', 'Weeks'
        MONTHS = 'MONTHS', 'Months'
        YEARS = 'YEARS', 'Years'

    type = models.CharField(
        max_length=20,
        choices=RecurrenceType.choices,
        default=RecurrenceType.DAYS,
        verbose_name="Recurrence Type"
    )
    interval = models.PositiveIntegerField(
        default=1,
        verbose_name="Interval (e.g., every X days/weeks/months)"
    )

    def __str__(self):
        return f"Recurrence Rule: {self.type}, Interval: {self.interval}"


class Event(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="User")
    name = models.CharField(max_length=255, default="Untitled", verbose_name="Event Name")
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name="Location")

    day = models.DateField(default=timezone.now, verbose_name="Event Day (No time)")

    start_time = models.TimeField(verbose_name="Start Time")
    end_time = models.TimeField(null=True, blank=True, default="01:00:00", verbose_name="End Time")
    recurrence_rule = models.ForeignKey(
        RecurrenceRule,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
        verbose_name="Recurrence Rule"
    )

    def __str__(self):
        return f"Event: {self.name}, on {self.day} from {self.start_time} to {self.end_time}"
