from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from Glassync.models import Notification


@csrf_exempt
@login_required
@require_POST
def get(request):
    """
    Returns all notifications for the currently logged-in user.
    """
    user = request.user
    notifications = Notification.objects.filter(id_user=user).order_by('-timestamp')

    notifications_data = []
    for n in notifications:
        notifications_data.append({
            'id': n.id,
            'timestamp': n.timestamp.isoformat(),
            'type': n.type,
            'event_id': n.id_event_id,
            'sender_id': n.id_user_sender_id,
        })

    return JsonResponse({'notifications': notifications_data}, status=200)