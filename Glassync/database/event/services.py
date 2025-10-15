from Glassync.models import Event, EventMember
from Glassync.database.friendship.services import are_friends
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist


def create_event(name, description, date, time_start, time_end, recurrence_rule_type, recurrence_rule_interval, creator):
    """
    Handles the creation of an event in the database.

    Args:
        name (str): The name of the event.
        description (str): The description of the event.
        date (str): The event's date (in 'YYYY-MM-DD' format).
        time_start (str): The start time (in 'HH:MM:SS' format, or None).
        time_end (str): The end time (in 'HH:MM:SS' format, or None).
        recurrence_rule_type (str): The recurrence rule type (daily/weekly/monthly).
        recurrence_rule_interval (int): The recurrence rule interval.
        creator (User): The user creating the event.

    Returns:
        dict: A dictionary with either the created event object or error details.
    """
    # Validate required fields
    if not all([name, date]):
        return {'error': 'Missing required fields: name or date', 'status': 400}

    # Validate time_start and time_end
    time_start_obj, time_end_obj = None, None
    if time_start and time_end:
        try:
            time_start_obj = datetime.strptime(time_start, '%H:%M:%S').time()
            time_end_obj = datetime.strptime(time_end, '%H:%M:%S').time()
            if time_start_obj >= time_end_obj:
                return {'error': 'time_start must be earlier than time_end', 'status': 400}
        except ValueError:
            return {'error': 'Invalid time format. Use HH:MM:SS', 'status': 400}

    # Validate recurrence_rule_type
    valid_recurrence_rule_types = ["daily", "weekly", "monthly"]
    if recurrence_rule_type and recurrence_rule_type not in valid_recurrence_rule_types:
        return {'error': f'Invalid recurrence_rule_type. Must be one of {valid_recurrence_rule_types}', 'status': 400}

    # Validate recurrence_rule_interval
    if recurrence_rule_interval is not None:
        try:
            recurrence_rule_interval = int(recurrence_rule_interval)
            if recurrence_rule_interval <= 0 or recurrence_rule_interval > 1000:  # Example limit
                return {'error': 'recurrence_rule_interval must be a positive integer and less than or equal to 1000', 'status': 400}
        except ValueError:
            return {'error': 'recurrence_rule_interval must be a valid integer', 'status': 400}

    # Convert date field
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return {'error': 'Invalid date format. Use YYYY-MM-DD', 'status': 400}

    # Create the event
    event = Event.objects.create(
        name=name,
        description=description,
        date=date,
        time_start=time_start_obj if time_start else None,
        time_end=time_end_obj if time_end else None,
        recurrence_rule_type=recurrence_rule_type,
        recurrence_rule_interval=recurrence_rule_interval,
        creator=creator
    )

    # Return the created event
    return {'event': event, 'status': 201}


def can_view_event(user_id, event_id):
    """
    Determines if a user can view an event.

    A user can view an event if:
    - They are the creator of the event.
    - They are a member of the event (a row exists in EventMember with id_event and id_user).

    Args:
        user_id (int): The ID of the user.
        event_id (int): The ID of the event.

    Returns:
        bool: True if the user can view the event, False otherwise.
    """
    try:
        # Check if the user is the creator of the event
        if Event.objects.filter(id=event_id, creator_id=user_id).exists():
            return True

        # Check if the user is a member of the event
        if EventMember.objects.filter(id_event_id=event_id, id_user_id=user_id).exists():
            return True

    except ObjectDoesNotExist:
        pass

    # If neither condition is met, the user cannot view the event
    return False


def get_event_by_uids(user_uid, event_uids, detailed=False):
    """
    Fetch events by a list of event UIDs, ensuring the user has access to view them.

    Args:
        user_uid (int): The ID of the user requesting the events.
        event_uids (list[int]): List of event UIDs to fetch.
        detailed (bool): Whether to include detailed information.

    Returns:
        list[dict]: List of event data or detailed event data for accessible events.
    """
    try:
        events = Event.objects.filter(id__in=event_uids)
        result = []

        for event in events:
            # Check if the user can view the event
            if can_view_event(user_uid, event.id):
                if detailed:
                    result.append({
                        "id": event.id,
                        "name": event.name,
                        "description": event.description,
                        "date": event.date,
                        "time_start": event.time_start,
                        "time_end": event.time_end,
                        "recurrence_rule_type": event.recurrence_rule_type,
                        "recurrence_rule_interval": event.recurrence_rule_interval,
                        "creator_id": event.creator_id,
                    })
                else:
                    result.append({
                        "id": event.id,
                        "name": event.name,
                        "date": event.date,
                    })

        return result

    except ObjectDoesNotExist:
        return []


def get_event_by_user_and_date(own_uid, user_uid, start_datetime, end_datetime, detailed=False):
    """
    Fetch events for a specific user within a given time range, ensuring access is allowed.

    Args:
        own_uid (int): Your user ID.
        user_uid (int): The UID of the user whose events to fetch.
        start_datetime (datetime): Start of the search range.
        end_datetime (datetime): End of the search range.
        detailed (bool): Whether to include detailed information.

    Returns:
        list[dict]: List of event data or detailed event data.
    """
    # Check if the user has access to view events
    if own_uid != user_uid and not are_friends(own_uid, user_uid):
        return []  # Access denied

    try:
        # Fetch events where user_uid is the creator
        creator_events = Event.objects.filter(
            creator_id=user_uid,
            date__range=[start_datetime.date(), end_datetime.date()],
            time_start__gte=start_datetime.time(),
            time_end__lte=end_datetime.time(),
        )

        # Fetch events where user_uid is a member and has accepted the invitation
        member_events = Event.objects.filter(
            id__in=EventMember.objects.filter(
                id_user_id=user_uid,
                accept_invitation=True
            ).values_list('id_event_id', flat=True),
            date__range=[start_datetime.date(), end_datetime.date()],
            time_start__gte=start_datetime.time(),
            time_end__lte=end_datetime.time(),
        )

        # Combine the two querysets and remove duplicates
        all_events = (creator_events | member_events).distinct()

        # Format the response
        if detailed:
            return [
                {
                    "id": event.id,
                    "name": event.name,
                    "description": event.description,
                    "date": event.date,
                    "time_start": event.time_start,
                    "time_end": event.time_end,
                    "recurrence_rule_type": event.recurrence_rule_type,
                    "recurrence_rule_interval": event.recurrence_rule_interval,
                    "creator_id": event.creator_id,
                }
                for event in all_events
            ]
        else:
            return [{"id": event.id, "name": event.name, "date": event.date} for event in all_events]

    except Exception as e:
        # Handle any unexpected errors
        return []