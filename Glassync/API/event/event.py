from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime
from Glassync.models import Event, User


@csrf_protect
@login_required
def create(request):
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

            # Validate required fields
            if not all([name, date]):
                return JsonResponse({'error': 'Missing required fields: name or date'}, status=400)

            # Validate time_start and time_end
            if time_start and time_end:
                time_start_obj = datetime.strptime(time_start, '%H:%M:%S').time()
                time_end_obj = datetime.strptime(time_end, '%H:%M:%S').time()
                if time_start_obj >= time_end_obj:
                    return JsonResponse({'error': 'time_start must be earlier than time_end'}, status=400)

            # Validate recurrence_rule_type
            valid_recurrence_rule_types = ["daily", "weekly", "monthly"]
            if recurrence_rule_type and recurrence_rule_type not in valid_recurrence_rule_types:
                return JsonResponse({'error': f'Invalid recurrence_rule_type. Must be one of {valid_recurrence_rule_types}'}, status=400)

            # Validate recurrence_rule_interval
            if recurrence_rule_interval is not None:
                try:
                    recurrence_rule_interval = int(recurrence_rule_interval)
                    if recurrence_rule_interval <= 0 or recurrence_rule_interval > 1000:  # Example limit
                        return JsonResponse({'error': 'recurrence_rule_interval must be a positive integer and less than or equal to 1000'}, status=400)
                except ValueError:
                    return JsonResponse({'error': 'recurrence_rule_interval must be a valid integer'}, status=400)

            # Automatically set the creator to the logged-in user
            creator = request.user

            # Convert date field
            try:
                date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

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