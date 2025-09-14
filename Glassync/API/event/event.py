from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from Glassync.database.event.services import create_event
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
            result = create_event(
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


def get(request):
    data = {'message': 'OK'}
    return JsonResponse(data, status=200)


def update(request):
    data = {'message': 'OK'}
    return JsonResponse(data, status=200)


def delete(request):
    data = {'message': 'OK'}
    return JsonResponse(data, status=200)


def action(request):
    data = {'message': 'OK'}
    return JsonResponse(data, status=200)