import json
from datetime import datetime
from typing import Dict, Any, List

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from Glassync.API.errors import ERRORS
from Glassync.database.event.services import (
    create_or_update_event,
    get_event_by_uids,
    get_event_by_user_and_date,
    delete_event,
)
from Glassync.database.event.actions import (
    accept_group_event_invite,
    decline_group_event_invite,
    quit_group_event,
    invite_to_group_event,
)
from Glassync.database.notification.services import set_event_notification_interval, delete_event_notification


def json_response(data, status=200):
    return JsonResponse(data, status=status, content_type="application/json")


@csrf_exempt
@login_required
@require_POST
def create(request: HttpRequest):
    """
    Create a new event.
    Expects: name, date, etc.
    """
    try:
        data = json.loads(request.body)
        errors = collect_event_field_errors(data, require_name=True, require_date=True)
        if errors:
            return json_response({'errors': errors, "status": 400}, status=400)

        result = create_or_update_event(
            name=data.get("name"),
            description=data.get("description", ""),
            date=data.get("date"),
            time_start=data.get("time_start"),
            time_end=data.get("time_end"),
            recurrence_rule_type=data.get("recurrence_rule_type"),
            recurrence_rule_interval=data.get("recurrence_rule_interval"),
            creator=request.user
        )
        if 'errors' in result:
            return json_response({'errors': result['errors'], 'status': result.get('status', 400)}, status=result.get('status', 400))

        # Handle personal_notifications (call set_event_notification_interval for each)
        personal_notifications = data.get("notifications", [])
        personal_notif_errors = []
        event_id = result['event'].id
        user_id = request.user.id
        for interval in personal_notifications:
            set_result = set_event_notification_interval(event_id, user_id, interval)
            if "errors" in set_result:
                personal_notif_errors.append(set_result["errors"])

        if personal_notif_errors:
            return json_response({'errors': personal_notif_errors, 'status': 400}, status=400)

        return json_response({
            'message': 'Event created successfully',
            'event_id': result['event'].id,
            'status': result['status']
        }, status=result['status'])
    except json.JSONDecodeError:
        return json_response({'errors': [ERRORS["general"]["invalid_json"]], "status": 400}, status=400)
    except Exception as e:
        return json_response({'errors': [dict(ERRORS["general"]["unexpected_error"], details=str(e))], "status": 500}, status=500)


@csrf_exempt
@login_required
@require_POST
def get(request: HttpRequest):
    """
    Get events by UID(s) or by user+date range.
    """
    try:
        data = json.loads(request.body)
        if "event_uids" in data:
            result = get_event_by_uids(
                user_uid=request.user.id,
                event_uids=data.get("event_uids", []),
                detailed=data.get("detailed", False)
            )
        elif "user_uid" in data and "start_date" in data and "end_date" in data:
            result = get_event_by_user_and_date(
                own_uid=request.user.id,
                user_uid=data["user_uid"],
                start_date=datetime.fromisoformat(data["start_date"]).date(),
                end_date=datetime.fromisoformat(data["end_date"]).date(),
                detailed=data.get("detailed", False)
            )
        else:
            errors = []
            if not data.get("event_uids"):
                errors.append(ERRORS["fields"]["missing_event_id"])
            if not data.get("user_uid") or not data.get("start_date") or not data.get("end_date"):
                errors.append(ERRORS["fields"]["missing_date"])
            return json_response({'errors': errors, "status": 400}, status=400)

        return json_response({'events': result, "status": 200}, status=200)
    except json.JSONDecodeError:
        return json_response({'errors': [ERRORS["general"]["invalid_json"]], "status": 400}, status=400)
    except ValueError as e:
        return json_response({'errors': [dict(ERRORS["fields"]["invalid_date_format"], details=str(e))], "status": 400}, status=400)
    except Exception as e:
        return json_response({'errors': [dict(ERRORS["general"]["unexpected_error"], details=str(e))], "status": 500}, status=500)


@csrf_exempt
@login_required
@require_POST
def update(request: HttpRequest):
    """
    Update an existing event.
    """
    try:
        data = json.loads(request.body)
        errors = []
        if not data.get("event_id"):
            errors.append(ERRORS["fields"]["missing_event_id"])
        if errors:
            return json_response({'errors': errors, "status": 400}, status=400)

        result = create_or_update_event(
            event_id=data.get("event_id"),
            name=data.get("name"),
            description=data.get("description", ""),
            date=data.get("date"),
            time_start=data.get("time_start"),
            time_end=data.get("time_end"),
            recurrence_rule_type=data.get("recurrence_rule_type"),
            recurrence_rule_interval=data.get("recurrence_rule_interval"),
            user_id=request.user.id
        )
        if 'errors' in result:
            return json_response({'errors': result['errors'], 'status': result.get('status', 400)}, status=result.get('status', 400))

        # Handle personal_notifications (call set_event_notification_interval for each)
        personal_notifications = data.get("notifications", [])
        personal_notif_errors = []
        event_id = result['event'].id
        user_id = request.user.id

        # Delete all existing notification settings/tasks for this user and event first
        delete_event_notification(user_id, event_id)

        for interval in personal_notifications:
            set_result = set_event_notification_interval(event_id, user_id, interval)
            if "errors" in set_result:
                personal_notif_errors.append(set_result["errors"])

        if personal_notif_errors:
            return json_response({'errors': personal_notif_errors, 'status': 400}, status=400)

        return json_response({
            'message': 'Event updated successfully',
            'event_id': result['event'].id,
            'status': result['status']
        }, status=result['status'])
    except json.JSONDecodeError:
        return json_response({'errors': [ERRORS["general"]["invalid_json"]], "status": 400}, status=400)
    except Exception as e:
        return json_response({'errors': [dict(ERRORS["general"]["unexpected_error"], details=str(e))], "status": 500}, status=500)


@csrf_exempt
@login_required
@require_POST
def delete(request: HttpRequest):
    """
    Delete an event.
    """
    try:
        data = json.loads(request.body)
        errors = []
        if not data.get("event_id"):
            errors.append(ERRORS["fields"]["missing_event_id"])
        if errors:
            return json_response({'errors': errors, "status": 400}, status=400)
        result = delete_event(
            event_id=data.get("event_id"),
            user_id=request.user.id
        )
        if 'errors' in result:
            return json_response({'errors': result['errors'], 'status': result.get('status', 400)}, status=result.get('status', 400))

        return json_response({'message': result['message'], "status": result['status']}, status=result['status'])
    except json.JSONDecodeError:
        return json_response({'errors': [ERRORS["general"]["invalid_json"]], "status": 400}, status=400)
    except Exception as e:
        return json_response({'errors': [dict(ERRORS["general"]["unexpected_error"], details=str(e))], "status": 500}, status=500)


@csrf_exempt
@login_required
@require_POST
def action(request: HttpRequest):
    """
    Perform an event-related action (invite, accept/decline invite, quit).
    """
    try:
        body = json.loads(request.body)
        event_id = body.get('event_id')
        action_type = body.get('action')
        extra_data = body.get('extra_data', {})

        errors = []
        if not event_id:
            errors.append(ERRORS["fields"]["missing_event_id"])
        if not action_type:
            errors.append(ERRORS["fields"]["missing_action"])
        if action_type == 'invite' and not extra_data.get('user_id'):
            errors.append(ERRORS["fields"]["missing_user_id"])
        if errors:
            return json_response({'errors': errors, "status": 400}, status=400)

        action_map = {
            'invite': invite_to_group_event,
            'accept_invite': accept_group_event_invite,
            'decline_invite': decline_group_event_invite,
            'quit': quit_group_event,
        }

        if action_type not in action_map:
            return json_response({'errors': [ERRORS["fields"]["invalid_action"]], "status": 400}, status=400)

        if action_type == 'invite':
            invitee_id = extra_data.get('user_id')
            result = action_map[action_type](
                user_owner=request.user.id,
                user_id=invitee_id,
                event_id=event_id
            )
        elif action_type == 'accept_invite':
            # Pass notifications if present in extra_data
            notifications = extra_data.get('notifications', None)
            result = action_map[action_type](
                user_id=request.user.id,
                event_id=event_id,
                notifications=notifications
            )
        else:
            result = action_map[action_type](
                user_id=request.user.id,
                event_id=event_id
            )

        if 'errors' in result:
            return json_response({'errors': result['errors'], 'status': result.get('status', 400)}, status=result.get('status', 400))

        return json_response(result, status=result.get('status', 500))
    except json.JSONDecodeError:
        return json_response({'errors': [ERRORS["general"]["invalid_json"]], "status": 400}, status=400)
    except Exception as e:
        return json_response({'errors': [dict(ERRORS["general"]["unexpected_error"], details=str(e))], "status": 500}, status=500)


def collect_event_field_errors(
    data: Dict[str, Any], require_name: bool = False, require_date: bool = False
) -> List[dict]:
    errors = []
    if require_name and not data.get("name"):
        errors.append(ERRORS["fields"]["missing_name"])
    if require_date and not data.get("date"):
        errors.append(ERRORS["fields"]["missing_date"])
    return errors