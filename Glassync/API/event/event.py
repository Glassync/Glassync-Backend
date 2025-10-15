from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from Glassync.database.event.services import create_or_update_event, get_event_by_uids, get_event_by_user_and_date, delete_event
from datetime import datetime
import json


@csrf_protect
@login_required
def create(request):
    """
    Handles the HTTP request for creating an event, delegates to `create_event`.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response with the result of the operation.
    """
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)

            # Extract parameters
            name = data.get("name")
            description = data.get("description", "")
            date = data.get("date")
            time_start = data.get("time_start", None)
            time_end = data.get("time_end", None)
            recurrence_rule_type = data.get("recurrence_rule_type", None)
            recurrence_rule_interval = data.get("recurrence_rule_interval", None)

            # Call the create_event function
            result = create_or_update_event(
                name=name,
                description=description,
                date=date,
                time_start=time_start,
                time_end=time_end,
                recurrence_rule_type=recurrence_rule_type,
                recurrence_rule_interval=recurrence_rule_interval,
                creator=request.user
            )

            # Check for errors in the result
            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=result['status'])

            # Success response
            return JsonResponse({
                'message': 'Event created successfully',
                'event_id': result['event'].id
            }, status=result['status'])

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    # Return error if not POST method
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_protect
@login_required
def get(request):
    """
    Handles the HTTP request for retrieving events.

    Decides between `get_event_by_uids` or `get_event_by_user_and_date` based on the provided JSON payload.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response with the list of events or error details.
    """
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)

            # Determine which function to use based on the provided keys
            if "event_uids" in data:
                # Use get_event_by_uids
                event_uids = data.get("event_uids", [])
                detailed = data.get("detailed", False)
                result = get_event_by_uids(user_uid=request.user.id, event_uids=event_uids, detailed=detailed)
            elif "user_uid" in data and "start_datetime" in data and "end_datetime" in data:
                # Use get_event_by_user_and_date
                own_uid = request.user.id
                user_uid = data["user_uid"]
                start_datetime = datetime.fromisoformat(data["start_datetime"])
                end_datetime = datetime.fromisoformat(data["end_datetime"])
                detailed = data.get("detailed", False)
                result = get_event_by_user_and_date(own_uid=own_uid, user_uid=user_uid, start_datetime=start_datetime,
                                                    end_datetime=end_datetime, detailed=detailed)
            else:
                # Invalid input
                return JsonResponse({'error': 'Invalid input. Provide either "event_uids" or "user_uid" with date range.'},
                                    status=400)

            # Success response
            return JsonResponse({'events': result}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except ValueError as e:
            return JsonResponse({'error': 'Invalid date format. Use ISO 8601 format.', 'details': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

    # Return error if not POST method
    return JsonResponse({'error': 'Invalid request method'}, status=405)


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
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)

            # Extract parameters
            event_id = data.get("event_id")
            name = data.get("name")
            description = data.get("description", "")
            date = data.get("date")
            time_start = data.get("time_start", None)
            time_end = data.get("time_end", None)
            recurrence_rule_type = data.get("recurrence_rule_type", None)
            recurrence_rule_interval = data.get("recurrence_rule_interval", None)

            # Call the update_event function
            result = create_or_update_event(
                event_id=event_id,
                name=name,
                description=description,
                date=date,
                time_start=time_start,
                time_end=time_end,
                recurrence_rule_type=recurrence_rule_type,
                recurrence_rule_interval=recurrence_rule_interval,
                user_id=request.user.id
            )

            # Check for errors in the result
            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=result['status'])

            # Success response
            return JsonResponse({
                'message': 'Event updated successfully',
                'event_id': result['event'].id
            }, status=result['status'])

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

    # Return error if not POST method
    return JsonResponse({'error': 'Invalid request method'}, status=405)


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
    if request.method == 'DELETE':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            event_id = data.get("event_id")

            # Call the delete_event function
            result = delete_event(event_id=event_id, user_id=request.user.id)

            # Check for errors in the result
            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=result['status'])

            # Success response
            return JsonResponse({'message': result['message']}, status=result['status'])

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

    # Return error if not DELETE method
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def action(request):
    data = {'message': 'OK'}
    return JsonResponse(data, status=200)