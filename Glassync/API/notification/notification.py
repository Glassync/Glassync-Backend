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
    # Retrieve notifications where the user is the recipient
    notifications = Notification.objects.filter(id_user=user).order_by('-timestamp')

    # Serialize notifications (customize fields as needed)
    notifications_data = []
    for n in notifications:
        notifications_data.append({
            'id': n.id,
            'timestamp': n.timestamp.isoformat(),
            'type': n.type,
            'event_id': n.id_event.id if n.id_event else None,
            'sender_id': n.id_user_sender.id if n.id_user_sender else None,
        })

    return JsonResponse({'notifications': notifications_data}, status=200)