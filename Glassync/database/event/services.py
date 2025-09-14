from Glassync.models import Event
from datetime import datetime


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