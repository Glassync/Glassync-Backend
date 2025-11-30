import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from Glassync.API.errors import ERRORS
from Glassync.database.notification.platform import update_all_tasks
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
def update(request: HttpRequest):
    """
    Updates multiple UserNotificationSettings for the current user.
    Expects JSON body: {
      "platforms": {
         "1": {"active": true},
         "2": {"active": false}
      }
    }
    """
    try:
        body = json.loads(request.body)
        user = request.user
        platforms_data = body.get("platforms")
        if not platforms_data or not isinstance(platforms_data, dict):
            return JsonResponse(
                {"errors": [{
                    **ERRORS["notification_settings"]["missing_platform_name"],
                    "detail": "Missing or invalid 'platforms' object in request."
                }]},
                status=400
            )

        errors = []
        updated_settings = []
        any_changed = False

        for platform_id_str, data in platforms_data.items():
            try:
                platform_id = int(platform_id_str)
            except ValueError:
                errors.append({
                    **ERRORS["notification_settings"]["platform_not_found"],
                    "detail": f"Platform ID '{platform_id_str}' is not a valid integer."
                })
                continue

            try:
                platform = NotificationPlatform.objects.get(id=platform_id)
            except NotificationPlatform.DoesNotExist:
                errors.append({
                    **ERRORS["notification_settings"]["platform_not_found"],
                    "detail": f"Platform ID {platform_id} not found."
                })
                continue

            try:
                setting = UserNotificationSettings.objects.get(id_user=user, id_notification_platform=platform)
            except UserNotificationSettings.DoesNotExist:
                errors.append({
                    **ERRORS["notification_settings"]["user_setting_not_found"],
                    "detail": f"User notification setting for platform ID {platform_id} not found."
                })
                continue

            old_active = setting.active
            # 'active' is required in each platform data
            if "active" not in data:
                errors.append({
                    **ERRORS["notification_settings"]["missing_platform_name"],
                    "detail": f"Missing 'active' field for platform ID {platform_id}."
                })
                continue

            new_active = bool(data["active"])
            if old_active != new_active:
                setting.active = new_active
                setting.save()
                any_changed = True

            updated_settings.append({
                "id": setting.id,
                "id_notification_platform": setting.id_notification_platform_id,
                "active": setting.active,
            })

        if any_changed:
            update_all_tasks(user.id)

        response = {
            "notification_settings": updated_settings
        }
        if errors:
            response["errors"] = errors

        return JsonResponse(response, status=200 if not errors else 207)

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
