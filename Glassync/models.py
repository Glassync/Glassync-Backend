from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    nickname = models.CharField(max_length=255, null=True, blank=True)
    avatar_path = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    username = None


class Event(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField()
    time_start = models.TimeField(null=True, blank=True)
    time_end = models.TimeField(null=True, blank=True)
    recurrence_rule_type = models.CharField(max_length=255, null=True, blank=True)
    recurrence_rule_interval = models.IntegerField(null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_events")
    notifications = models.JSONField(null=True, blank=True)


class Notification(models.Model):
    id = models.BigAutoField(primary_key=True)
    timestamp = models.DateTimeField()
    type = models.CharField(max_length=255)
    id_event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class EventMember(models.Model):
    id_event = models.ForeignKey(Event, on_delete=models.CASCADE)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    accept_invitation = models.BooleanField(default=False)

    class Meta:
        unique_together = ('id_event', 'id_user')


class NotificationPlatform(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)


class UserNotificationSettings(models.Model):
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_notification_platform = models.ForeignKey(NotificationPlatform, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    attr = models.CharField(max_length=255)

    class Meta:
        unique_together = ('id_user', 'id_notification_platform')


class UsersRelationship(models.Model):
    id_user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="relationships_initiated")
    id_user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="relationships_received")
    status_user1 = models.BooleanField()
    status_user2 = models.BooleanField()

    class Meta:
        unique_together = ('id_user1', 'id_user2')


class UserEventNotificationSettings(models.Model):
    id_event = models.ForeignKey(Event, on_delete=models.CASCADE)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_rule_type = models.CharField(max_length=255, null=True, blank=True)
    notification_rule_interval = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('id_event', 'id_user')


class Task(models.Model):
    time = models.TimeField()
    id_event = models.ForeignKey(Event, on_delete=models.CASCADE)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.ForeignKey(NotificationPlatform, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('time', 'id_event', 'id_user', 'platform')