from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from Glassync.database.event.services import create_or_update_event, get_event_by_uids, get_event_by_user_and_date, delete_event
from Glassync.database.event.actions import accept_group_event_invite, decline_group_event_invite, quit_group_event, invite_to_group_event
from datetime import datetime
import json


@csrf_protect
@login_required
def create(request):
    """
    Handles the HTTP request for creating an event, including optional notification intervals.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response with the result of the operation.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method, only POST is allowed'}, status=405)

    try:
        data = json.loads(request.body)

        result = create_or_update_event(
            name=data.get("name"),
            description=data.get("description", ""),
            date=data.get("date"),
            time_start=data.get("time_start"),
            time_end=data.get("time_end"),
            recurrence_rule_type=data.get("recurrence_rule_type"),
            recurrence_rule_interval=data.get("recurrence_rule_interval"),
            creator=request.user,
            notifications=data.get("notifications", [])
        )
        if 'error' in result:
            return JsonResponse({'error': result['error']}, status=result['status'])

        return JsonResponse({
            'message': 'Event created successfully',
            'event_id': result['event'].id
        }, status=result['status'])

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)


@csrf_protect
@login_required
def get(request):
    """
    Handles the HTTP request for retrieving events.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response with the list of events or error details.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method, only POST is allowed'}, status=405)

    try:
        data = json.loads(request.body)
        if "event_uids" in data:
            result = get_event_by_uids(
                user_uid=request.user.id,
                event_uids=data.get("event_uids", []),
                detailed=data.get("detailed", False)
            )
        elif "user_uid" in data and "start_date" in data and "end_date" in data:
            # Adjusted to handle start_date and end_date
            result = get_event_by_user_and_date(
                own_uid=request.user.id,
                user_uid=data["user_uid"],
                start_date=datetime.fromisoformat(data["start_date"]).date(),
                end_date=datetime.fromisoformat(data["end_date"]).date(),
                detailed=data.get("detailed", False)
            )
        else:
            return JsonResponse({'error': 'Invalid input. Provide either "event_uids" or "user_uid" with date range.'},
                                status=400)

        return JsonResponse({'events': result}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except ValueError as e:
        return JsonResponse({'error': f'Invalid date format: {str(e)}. Use ISO 8601 format.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)


@csrf_protect
@login_required
def update(request):
    """
    Handles the HTTP request for updating an event.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response with the result of the operation.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method, only POST is allowed'}, status=405)

    try:
        data = json.loads(request.body)
        notifications = data.get("notifications", [])  # <-- add this line

        result = create_or_update_event(
            event_id=data.get("event_id"),
            name=data.get("name"),
            description=data.get("description", ""),
            date=data.get("date"),
            time_start=data.get("time_start"),
            time_end=data.get("time_end"),
            recurrence_rule_type=data.get("recurrence_rule_type"),
            recurrence_rule_interval=data.get("recurrence_rule_interval"),
            user_id=request.user.id,
            notifications=notifications   # <-- and this line
        )
        if 'error' in result:
            return JsonResponse({'error': result['error']}, status=result['status'])

        return JsonResponse({
            'message': 'Event updated successfully',
            'event_id': result['event'].id
        }, status=result['status'])

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)


@csrf_protect
@login_required
def delete(request):
    """
    Handles the HTTP request for deleting an event.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response with the result of the operation.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method, only POST is allowed'}, status=405)

    try:
        data = json.loads(request.body)
        result = delete_event(
            event_id=data.get("event_id"),
            user_id=request.user.id
        )
        if 'error' in result:
            return JsonResponse({'error': result['error']}, status=result['status'])

        return JsonResponse({'message': result['message']}, status=result['status'])

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)


@csrf_protect
@login_required
def action(request):
    """
    Handle group event-related actions dynamically.

    Args:
        request: The HTTP request containing `event_id`, `action`, and possibly additional data.

    Returns:
        JsonResponse: A JSON response with the result of the action.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method, only POST is allowed'}, status=405)

    try:
        body = json.loads(request.body)
        event_id = body.get('event_id')
        action_type = body.get('action')
        extra_data = body.get('extra_data', {})

        if not event_id or not action_type:
            return JsonResponse({'error': 'Missing required fields: event_id or action'}, status=400)

        action_map = {
            'invite': invite_to_group_event,
            'accept_invite': accept_group_event_invite,
            'decline_invite': decline_group_event_invite,
            'quit': quit_group_event,
        }

        if action_type not in action_map:
            return JsonResponse({'error': f'Invalid action: {action_type}'}, status=400)

        if action_type == 'invite':
            invitee_id = extra_data.get('user_id')
            if not invitee_id:
                return JsonResponse({'error': 'Missing user_id in extra_data for invite action'}, status=400)
            result = action_map[action_type](
                user_owner=request.user.id,
                user_id=invitee_id,
                event_id=event_id
            )
        else:
            result = action_map[action_type](
                user_id=request.user.id,
                event_id=event_id
            )

        return JsonResponse(result, status=result.get('status', 500))

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)