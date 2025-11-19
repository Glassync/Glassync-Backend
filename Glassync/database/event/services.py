from Glassync.database.notification.services import set_event_notification_interval
from Glassync.models import Event, EventMember
from Glassync.database.friendship.services import are_friends
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from Glassync.API.errors import ERRORS


def create_or_update_event(
    event_id=None,
    name=None,
    description=None,
    date=None,
    time_start=None,
    time_end=None,
    recurrence_rule_type=None,
    recurrence_rule_interval=None,
    creator=None,
    user_id=None,
    notifications=None,
):
    """
    Handles creating or updating an event in the database, including notification intervals.
    Returns: dict with either {'event': event_obj, 'status': int} or {'errors': [error_dicts], 'status': int}
    """
    errors = []

    if event_id:
        # Update existing event
        try:
            event = Event.objects.get(id=event_id)
        except ObjectDoesNotExist:
            return {'errors': [ERRORS["event"]["event_not_found"]], 'status': 404}

        if event.creator_id != user_id:
            return {'errors': [ERRORS["event"]["permission_denied"]], 'status': 403}
    else:
        # Create a new event
        if not creator:
            errors.append(ERRORS["fields"]["missing_creator"])
        event = Event(creator=creator) if creator else None

    # Validate required fields for creation
    if not event_id:
        if not name:
            errors.append(ERRORS["fields"]["missing_name"])
        if not date:
            errors.append(ERRORS["fields"]["missing_date"])

    # Validate time_start and time_end
    time_start_obj, time_end_obj = None, None
    if time_start and time_end:
        try:
            time_start_obj = datetime.strptime(time_start, '%H:%M:%S').time()
            time_end_obj = datetime.strptime(time_end, '%H:%M:%S').time()
            if time_start_obj >= time_end_obj:
                errors.append(ERRORS["fields"]["invalid_time_order"])
        except ValueError:
            errors.append(ERRORS["fields"]["invalid_time_format"])
    elif time_start or time_end:
        if not time_start:
            errors.append(ERRORS["fields"]["missing_time_start"])
        if not time_end:
            errors.append(ERRORS["fields"]["missing_time_end"])

    # Validate recurrence_rule_type and interval: both must be null or both must be not null
    if (recurrence_rule_type is None and recurrence_rule_interval is not None) or \
       (recurrence_rule_type is not None and recurrence_rule_interval is None):
        errors.append(ERRORS["fields"]["recurrence_type_and_interval_must_match"])

    # Validate recurrence_rule_type
    valid_recurrence_rule_types = ["daily", "weekly", "monthly", "yearly"]
    if recurrence_rule_type and recurrence_rule_type not in valid_recurrence_rule_types:
        errors.append(ERRORS["fields"]["invalid_recurrence_type"])

    # Validate recurrence_rule_interval
    if recurrence_rule_interval is not None:
        try:
            recurrence_rule_interval = int(recurrence_rule_interval)
            if recurrence_rule_interval <= 0 or recurrence_rule_interval > 1000:
                errors.append(ERRORS["fields"]["invalid_recurrence_interval"])
        except ValueError:
            errors.append(ERRORS["fields"]["invalid_recurrence_integer"])

    # Convert date field
    if date:
        try:
            event.date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            errors.append(ERRORS["fields"]["invalid_date_format"])

    if errors:
        return {'errors': errors, 'status': 400}

    # Update event fields
    if name is not None:
        event.name = name
    if description is not None:
        event.description = description
    if time_start_obj is not None:
        event.time_start = time_start_obj
    if time_end_obj is not None:
        event.time_end = time_end_obj
    if recurrence_rule_type is not None:
        event.recurrence_rule_type = recurrence_rule_type
    if recurrence_rule_interval is not None:
        event.recurrence_rule_interval = recurrence_rule_interval
    if notifications is not None:
        event.notifications = notifications

    # Validate notifications if provided
    if notifications is None:
        notifications = []

    if not isinstance(notifications, list):
        errors.append(ERRORS["fields"]["invalid_notification_entry"])
    else:
        for notif in notifications:
            try:
                notif_int = int(notif)
                if notif_int <= 0:
                    errors.append(ERRORS["fields"]["invalid_notification_interval"])
            except Exception:
                errors.append(ERRORS["fields"]["invalid_notification_interval"])

    event.save()

    # Notifications set up
    for notif in notifications:
        set_event_notification_interval(event.id, user_id, int(notif))

    return {'event': event, 'status': 201 if not event_id else 200}


def can_view_event(user_id, event_id):
    try:
        if Event.objects.filter(id=event_id, creator_id=user_id).exists():
            return True
        if EventMember.objects.filter(id_event_id=event_id, id_user_id=user_id).exists():
            return True
    except ObjectDoesNotExist:
        pass
    return False


def get_event_by_uids(user_uid, event_uids, detailed=False):
    try:
        events = Event.objects.filter(id__in=event_uids)
        result = {}
        for event in events:
            if can_view_event(user_uid, event.id):
                if detailed:
                    result[event.id] = {
                        "id": event.id,
                        "name": event.name,
                        "description": event.description,
                        "date": event.date,
                        "time_start": event.time_start,
                        "time_end": event.time_end,
                        "recurrence_rule_type": event.recurrence_rule_type,
                        "recurrence_rule_interval": event.recurrence_rule_interval,
                        "creator_id": event.creator_id,
                        "notifications": event.notifications,
                    }
                else:
                    result[event.id] = {
                        "id": event.id,
                        "name": event.name,
                        "date": event.date,
                    }
        return result
    except ObjectDoesNotExist:
        return {}
    except Exception as e:
        return {}


def get_event_by_user_and_date(own_uid, user_uid, start_date, end_date, detailed=False):
    if own_uid != user_uid and not are_friends(own_uid, user_uid):
        return {}

    try:
        # Single (non-repeating) events in date range
        creator_single = Event.objects.filter(
            creator_id=user_uid,
            date__range=[start_date, end_date],
            recurrence_rule_type__isnull=True,
            recurrence_rule_interval__isnull=True,
        )
        member_single = Event.objects.filter(
            id__in=EventMember.objects.filter(
                id_user_id=user_uid,
                accept_invitation=True
            ).values_list('id_event_id', flat=True),
            date__range=[start_date, end_date],
            recurrence_rule_type__isnull=True,
            recurrence_rule_interval__isnull=True,
        )

        # Recurrent (repeating) events, both recurrence fields NOT null
        creator_recurrent = Event.objects.filter(
            creator_id=user_uid,
            recurrence_rule_type__isnull=False,
            recurrence_rule_interval__isnull=False,
        )
        member_recurrent = Event.objects.filter(
            id__in=EventMember.objects.filter(
                id_user_id=user_uid,
                accept_invitation=True
            ).values_list('id_event_id', flat=True),
            recurrence_rule_type__isnull=False,
            recurrence_rule_interval__isnull=False,
        )
        all_events = (creator_single | member_single | creator_recurrent | member_recurrent).distinct()

        # Building the result
        result = {}
        for event in all_events:
            if detailed:
                result[event.id] = {
                    "id": event.id,
                    "name": event.name,
                    "description": event.description,
                    "date": event.date,
                    "time_start": event.time_start,
                    "time_end": event.time_end,
                    "recurrence_rule_type": event.recurrence_rule_type,
                    "recurrence_rule_interval": event.recurrence_rule_interval,
                    "creator_id": event.creator_id,
                    "notifications": event.notifications,
                }
            else:
                result[event.id] = {
                    "id": event.id,
                    "name": event.name,
                    "date": event.date,
                }

        return result

    except Exception as e:
        return {}


def delete_event(event_id, user_id):
    try:
        event = Event.objects.get(id=event_id)
        if event.creator_id != user_id:
            return {'errors': [ERRORS["event"]["permission_denied"]], 'status': 403}
        EventMember.objects.filter(id_event_id=event_id).delete()
        event.delete()
        return {'message': 'Event and associated members deleted successfully', 'status': 200}
    except ObjectDoesNotExist:
        return {'errors': [ERRORS["event"]["event_not_found"]], 'status': 404}