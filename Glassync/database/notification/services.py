from Glassync.API.errors import ERRORS
from Glassync.models import UserNotificationSettings, Task, UserEventNotificationSettings, Event, EventMember

from datetime import datetime, timedelta


def set_event_notification_interval(id_event, id_user, notification_interval_in_minutes):
    """
    Adds a notification interval for a user on a specific event.
    Allows multiple intervals per user/event pair.
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

    # Prevent duplicate intervals
    exists = UserEventNotificationSettings.objects.filter(
        id_event_id=id_event,
        id_user_id=id_user,
        notification_interval_in_minutes=interval
    ).exists()
    if exists:
        return {"message": "Notification interval already exists."}

    # Create new notification interval
    try:
        settings = UserEventNotificationSettings.objects.create(
            id_event_id=id_event,
            id_user_id=id_user,
            notification_interval_in_minutes=interval
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
    Deletes all tasks for a given user/event and re-creates them for each notification interval.
    """
    # Remove all tasks for this event/user
    Task.objects.filter(id_event=settings.id_event, id_user=settings.id_user).delete()

    # Get all user's active notification platforms
    active_platforms = UserNotificationSettings.objects.filter(
        id_user=settings.id_user,
        active=True,
    )

    # Find all UserEventNotificationSettings for this user/event
    all_settings = UserEventNotificationSettings.objects.filter(
        id_event=settings.id_event,
        id_user=settings.id_user
    )

    for notif_setting in all_settings:
        event_time = notif_setting.id_event.time_start
        event_date = notif_setting.id_event.date

        if not event_time or not event_date:
            # Optionally, log or handle this case: missing event time or date
            continue

        event_datetime = datetime.combine(event_date, event_time)
        notification_time = event_datetime - timedelta(minutes=notif_setting.notification_interval_in_minutes)

        # Create a task for each active platform
        for user_platform in active_platforms:
            Task.objects.create(
                time=notification_time,
                id_event=notif_setting.id_event,
                id_user=notif_setting.id_user,
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


def delete_event_notifications_for_all_users(event_id):
    """
    Deletes all UserEventNotificationSettings and Task entries for all users participating in a given event.
    """
    # Get the event
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return {"errors": ["Event does not exist."]}

    # Collect all user IDs: creator + members who accepted invitation
    user_ids = set()

    # Add the event creator
    if event.creator_id:
        user_ids.add(event.creator_id)

    # Add all accepted event members
    member_user_ids = (EventMember.objects.filter(id_event_id=event_id, accept_invitation=True).values_list("id_user_id", flat=True))
    user_ids.update(member_user_ids)

    # Delete notifications for all users
    for user_id in user_ids:
        delete_event_notification(user_id, event_id)

    return {"message": "Event notifications and tasks deleted for all users."}


def get_notification_times(user_id, event_id):
    """
    Returns a list of all notification intervals (in minutes) for a user and event.
    Example output: [20, 15, 30]
    """
    from Glassync.models import UserEventNotificationSettings

    # Query all notification settings for this user and event
    intervals = list(
        UserEventNotificationSettings.objects
        .filter(id_user_id=user_id, id_event_id=event_id)
        .values_list("notification_interval_in_minutes", flat=True)
    )
    return intervals