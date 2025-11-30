import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from Glassync.API.errors import ERRORS
from Glassync.models import UserNotificationSettings, NotificationPlatform


@csrf_exempt
@login_required
@require_POST
def get(request: HttpRequest):
    """
    Returns all notification settings for the current user, excluding the 'attr' field.
    """
    user = request.user
    settings = UserNotificationSettings.objects.filter(id_user=user)
    settings_list = []
    for s in settings:
        settings_list.append({
            'id': s.id,
            'id_notification_platform': s.id_notification_platform_id,
            'active': s.active,
        })
    return JsonResponse({'notification_settings': settings_list}, status=200)


@csrf_exempt
@login_required
@require_POST
def update_notification_setting(request: HttpRequest):
    """
    Updates the UserNotificationSettings for the current user and given notification platform (by name).
    Expects JSON body: {"platform_name": ..., "active": ..., "attr": ... (optional)}
    """
    try:
        body = json.loads(request.body)
        user = request.user
        platform_name = body.get("platform_name")
        if not platform_name:
            return JsonResponse(
                {"errors": [ERRORS["notification_settings"]["missing_platform_name"]]},
                status=400
            )

        try:
            platform = NotificationPlatform.objects.get(name=platform_name)
        except NotificationPlatform.DoesNotExist:
            return JsonResponse(
                {"errors": [ERRORS["notification_settings"]["platform_not_found"]]},
                status=404
            )

        try:
            setting = UserNotificationSettings.objects.get(id_user=user, id_notification_platform=platform)
        except UserNotificationSettings.DoesNotExist:
            return JsonResponse(
                {"errors": [ERRORS["notification_settings"]["user_setting_not_found"]]},
                status=404
            )

        # Update fields
        if "active" in body:
            setting.active = bool(body["active"])
        if "attr" in body:
            setting.attr = body["attr"]
        setting.save()

        result = {
            "id": setting.id,
            "id_notification_platform": setting.id_notification_platform_id,
            "active": setting.active,
        }
        return JsonResponse({"notification_setting": result}, status=200)

    except json.JSONDecodeError:
        return JsonResponse(
            {"errors": [ERRORS["general"]["invalid_json"]]},
            status=400
        )
    except Exception as e:
        error = dict(ERRORS["general"]["unexpected_error"], details=str(e))
        return JsonResponse(
            {"errors": [error]},
            status=500
        )
