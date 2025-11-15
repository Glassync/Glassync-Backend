import json

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from Glassync.API.errors import ERRORS
from Glassync.database.user.profile import (
    get_profile,
    update_profile,
    delete_profile,
)
from Glassync.database.user.search import find_users
from Glassync.database.friendship.services import (
    accept_friendship,
    decline_friendship,
    request_friendship,
    delete_friendship,
)

User = get_user_model()


def json_response(data: dict, status: int = 200):
    return JsonResponse(data, status=status, content_type="application/json")


@csrf_exempt
@login_required
@require_POST
def get(request: HttpRequest):
    """
    Retrieve the profiles of one or more users (by user_ids), or search for users based on filters via POST request.
    """
    try:
        body = json.loads(request.body)
        own_uid = request.user.id

        user_ids = body.get("user_ids")

        if user_ids is not None:
            if not isinstance(user_ids, list) or not user_ids:
                return json_response({"errors": [ERRORS["user"]["invalid_user_ids"]]}, status=400)

            users = {}
            errors = {}
            for uid in user_ids:
                profile, status_code = get_profile(own_uid=own_uid, user_id=uid)
                if status_code == 200:
                    users[str(uid)] = profile
                else:
                    errors[str(uid)] = profile.get("errors", [{
                        "code": "unknown_error",
                        "message_en": "Unknown error",
                        "message_ru": "Неизвестная ошибка"
                    }])
            if users and errors:
                return json_response({"users": users, "errors": errors}, status=206)
            elif users:
                return json_response({"users": users}, status=200)
            else:
                return json_response({"errors": errors}, status=404)

        # If no user_ids, handle search filters
        if "search_string" not in body:
            return json_response({"errors": [ERRORS["user"]["missing_search_string"]]}, status=400)
        request_string = body["search_string"]
        request_filter = body.get("request_filter", "all")
        relationship_filter = body.get("relationship_filter", "all")

        result, status_code = find_users(
            searcher_id=own_uid,
            request_string=request_string,
            relationship_filter=relationship_filter,
            request_filter=request_filter
        )
        return json_response(result, status=status_code)

    except json.JSONDecodeError:
        return json_response({"errors": [ERRORS["general"]["invalid_json"]]}, status=400)
    except ValueError:
        return json_response({"errors": [ERRORS["user"]["invalid_data_format"]]}, status=400)
    except Exception as e:
        return json_response({"errors": [dict(ERRORS["general"]["unexpected_error"], details=str(e))]}, status=500)


@csrf_exempt
@login_required
@require_POST
def update(request: HttpRequest):
    """
    Update the profile of the logged-in user, optionally including password change.
    """
    try:
        body = json.loads(request.body)
        user_id = request.user.id

        first_name = body.get("first_name")
        last_name = body.get("last_name")
        nickname = body.get("nickname")
        avatar_path = body.get("avatar_path")
        password = body.get("password")
        current_password = body.get("current_password")

        response, status_code = update_profile(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            nickname=nickname,
            avatar_path=avatar_path,
            password=password,
            current_password=current_password,
        )

        return json_response(response, status=status_code)
    except json.JSONDecodeError:
        return json_response({"errors": [ERRORS["general"]["invalid_json"]]}, status=400)
    except Exception as e:
        return json_response({"errors": [dict(ERRORS["general"]["unexpected_error"], details=str(e))]}, status=500)


@csrf_exempt
@login_required
@require_POST
def delete(request: HttpRequest):
    """
    Delete the profile of the logged-in user.
    """
    try:
        user_id = request.user.id
        response, status_code = delete_profile(user_id=user_id)
        return json_response(response, status=status_code)
    except Exception as e:
        return json_response({"errors": [dict(ERRORS["general"]["unexpected_error"], details=str(e))]}, status=500)


@csrf_exempt
@login_required
@require_POST
def action(request: HttpRequest):
    """
    Perform a friendship-related action (accept, decline, request, or delete friendship).
    The response always contains "user" with info about the requesting user.
    """
    try:
        data = json.loads(request.body)
    except Exception:
        return json_response(
            {"errors": [ERRORS["general"]["invalid_json"]]},
            status=400
        )

    errors = []
    action_str = data.get("action")
    user_id = data.get("user_id")

    # Validate 'action'
    if not action_str:
        errors.append(ERRORS["fields"]["missing_action"])
    elif action_str not in (
        "accept_friendship",
        "decline_friendship",
        "request_friendship",
        "delete_friendship"
    ):
        errors.append(ERRORS["fields"]["invalid_action"])

    # Validate 'user_id'
    if not user_id:
        errors.append(ERRORS["fields"]["missing_user_id"])

    if errors:
        return json_response({"errors": errors}, status=400)

    try:
        other_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return json_response(
            {"errors": [ERRORS["user"]["not_found"]]},
            status=404
        )

    # Call the correct friendship service function
    if action_str == "accept_friendship":
        result = accept_friendship(user_sender=other_user, user_accepted=request.user)
    elif action_str == "decline_friendship":
        result = decline_friendship(user_sender=other_user, user_declined=request.user)
    elif action_str == "request_friendship":
        result = request_friendship(user_sender=request.user, user_receiver=other_user)
    elif action_str == "delete_friendship":
        result = delete_friendship(user_sender=request.user, user_receiver=other_user)
    else:
        errors.append(ERRORS["fields"]["invalid_action"])
        profile, _ = get_profile(request.user.id, user_id)
        return json_response({"errors": errors, "user": profile}, status=400)

    result_errors = result.get("errors")
    if result_errors:
        if not isinstance(result_errors, list):
            result_errors = [result_errors]
        # Merge and deduplicate by code
        unique = {err["code"]: err for err in errors + result_errors}
        profile, _ = get_profile(request.user.id, user_id)
        return json_response({"errors": list(unique.values()), "user": profile}, status=result.get("status", 400))

    response = {k: v for k, v in result.items() if k != "status"}
    profile, _ = get_profile(request.user.id, user_id)
    response["user"] = profile
    return json_response(response, status=result.get("status", 200))
