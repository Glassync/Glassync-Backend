from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from Glassync.models import Event, User


@csrf_exempt
def create(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)

            # Extract parameters
            creator_id = data.get("creator_id")
            name = data.get("name")
            description = data.get("description", "")
            date = data.get("date")
            time_start = data.get("time_start", None)
            time_end = data.get("time_end", None)
            recurrence_rule_type = data.get("recurrence_rule_type", None)
            recurrence_rule_interval = data.get("recurrence_rule_interval", None)

            # Validate required fields
            if not all([creator_id, name, date]):
                return JsonResponse({'error': 'Missing required fields: creator_id, name, or date'}, status=400)

            # Validate creator existence
            try:
                creator = User.objects.get(id=creator_id)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Creator not found'}, status=404)

            # Convert date and time fields
            try:
                date = datetime.strptime(date, '%Y-%m-%d').date()
                if time_start:
                    time_start = datetime.strptime(time_start, '%H:%M:%S').time()
                if time_end:
                    time_end = datetime.strptime(time_end, '%H:%M:%S').time()
            except ValueError:
                return JsonResponse({'error': 'Invalid date or time format'}, status=400)

            # Create the event
            event = Event.objects.create(
                name=name,
                description=description,
                date=date,
                time_start=time_start,
                time_end=time_end,
                recurrence_rule_type=recurrence_rule_type,
                recurrence_rule_interval=recurrence_rule_interval,
                creator=creator
            )

            # Return success response
            return JsonResponse({
                'message': 'Event created successfully',
                'event_id': event.id
            }, status=201)

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