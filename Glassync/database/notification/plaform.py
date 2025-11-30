from Glassync.models import User, NotificationPlatform, UserNotificationSettings


def create_user_notification_settings_for_user(user_id):
    """
    Creates a UserNotificationSettings entry for each NotificationPlatform for the given user_id,
    if it does not already exist.
    """

    user = User.objects.get(id=user_id)
    platforms = NotificationPlatform.objects.all()
    created = []
    for platform in platforms:
        obj, was_created = UserNotificationSettings.objects.get_or_create(
            id_user=user,
            id_notification_platform=platform,
            defaults={'active': False, 'attr': None}
        )
        if was_created:
            created.append(obj)
    return created
