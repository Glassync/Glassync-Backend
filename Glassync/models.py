from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    nickname = models.CharField(max_length=255, null=True, blank=True)
    avatar_path = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = UserManager()


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
    notification_interval_in_minutes = models.BigIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('id_event', 'id_user')


class Task(models.Model):
    time = models.TimeField()
    id_event = models.ForeignKey(Event, on_delete=models.CASCADE)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.ForeignKey(NotificationPlatform, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('time', 'id_event', 'id_user', 'platform')