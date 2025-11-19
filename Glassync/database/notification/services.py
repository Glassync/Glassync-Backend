from Glassync.API.errors import ERRORS
from Glassync.models import UserNotificationSettings, Task, UserEventNotificationSettings

from datetime import datetime, timedelta


def set_event_notification_interval(id_event, id_user, notification_interval_in_minutes):
    """
    Sets the notification interval for a user on a specific event.
    """
    # Validate input
    try:
        interval = int(notification_interval_in_minutes)
        if interval <= 0:
            return {
                "errors": [ERRORS["fields"]["invalid_notification_interval"]]
            }
    except (TypeError, ValueError):
        return {
            "errors": [ERRORS["fields"]["invalid_notification_interval"]]
        }

    # Create or update UserEventNotificationSettings
    try:
        settings, _ = UserEventNotificationSettings.objects.update_or_create(
            id_event_id=id_event,
            id_user_id=id_user,
            defaults={"notification_interval_in_minutes": interval}
        )
    except Exception as e:
        return {
            "errors": [ERRORS["fields"]["user_event_notification_settings_failed"]],
            "details": str(e)
        }

    # Update tasks
    update_task(settings)

    return {"message": "Notification interval set successfully."}


def update_task(settings):
    """
    Updates notification tasks for a given user's event notification settings.
    """
    # Remove all tasks for this event/user
    Task.objects.filter(id_event=settings.id_event, id_user=settings.id_user).delete()

    # Get all user's active notification platforms
    active_platforms = UserNotificationSettings.objects.filter(
        id_user=settings.id_user,
        active=True,
    )

    # Get the event time and date
    event_time = settings.id_event.time_start
    event_date = settings.id_event.date

    if not event_time or not event_date:
        # Optionally, log or handle this case: missing event time or date
        return

    event_datetime = datetime.combine(event_date, event_time)
    notification_time = (event_datetime - timedelta(minutes=settings.notification_interval_in_minutes)).time()

    # Create a task for each platform
    for user_platform in active_platforms:
        Task.objects.create(
            time=notification_time,
            id_event=settings.id_event,
            id_user=settings.id_user,
            platform=user_platform.id_notification_platform,
        )


def delete_event_notification(user_id, event_id):
    """
    Deletes the UserEventNotificationSettings and all Task entries
    for the given user and event.
    """
    # Delete UserEventNotificationSettings
    UserEventNotificationSettings.objects.filter(
        id_user_id=user_id,
        id_event_id=event_id
    ).delete()

    # Delete all related tasks
    Task.objects.filter(
        id_user_id=user_id,
        id_event_id=event_id
    ).delete()

    return {"message": "Event notifications and tasks deleted successfully."}