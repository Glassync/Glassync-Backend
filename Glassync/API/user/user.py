from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from Glassync.database.user.profile import get_profile, update_profile, delete_profile
from Glassync.database.user.search import find_users
import json


@csrf_protect
@login_required
def get(request):
    """
    Retrieve the profiles of one or more users (by user_ids), or search for users based on filters via POST request.

    Args:
        request: The HTTP request object containing 'user_ids' or search filter parameters in the body.

    Returns:
        JsonResponse: The users' profiles, a list of users, or an error message.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method, only POST is allowed"}, status=405)

    try:
        body = json.loads(request.body)
        own_uid = request.user.id

        user_ids = body.get("user_ids")

        if user_ids is not None:
            if not isinstance(user_ids, list) or not user_ids:
                return JsonResponse({"error": "'user_ids' must be a non-empty list of user IDs"}, status=400)

            users = {}
            errors = {}
            for uid in user_ids:
                profile, status_code = get_profile(own_uid=own_uid, user_id=uid)
                if status_code == 200:
                    users[str(uid)] = profile
                else:
                    errors[str(uid)] = profile.get("error", "Unknown error")
            if users and errors:
                return JsonResponse({"users": users, "errors": errors}, status=206)
            elif users:
                return JsonResponse({"users": users}, status=200)
            else:
                return JsonResponse({"error": errors}, status=404)

        # If no user_ids, handle search filters as before
        if "search_string" not in body:
            return JsonResponse({"error": "Missing 'search_string' in request body"}, status=400)
        request_string = body["search_string"]
        request_filter = body.get("request_filter", "all")
        relationship_filter = body.get("relationship_filter", "all")

        result, status_code = find_users(
            searcher_id=own_uid,
            request_string=request_string,
            relationship_filter=relationship_filter,
            request_filter=request_filter
        )
        return JsonResponse(result, status=status_code)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    except ValueError:
        return JsonResponse({"error": "Invalid data format in request"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


@csrf_protect
@login_required
def update(request):
    """
    Update the profile of the logged-in user.

    Args:
        request: The HTTP request object containing the fields to update.

    Returns:
        JsonResponse: A success message or an error message.
    """
    # Enforce the POST method
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method, only POST is allowed"}, status=405)

    try:
        # Parse the JSON body to get the fields to update
        body = json.loads(request.body)
        user_id = request.user.id

        first_name = body.get("first_name")
        last_name = body.get("last_name")
        nickname = body.get("nickname")
        avatar_path = body.get("avatar_path")

        # Update the user's profile
        response, status_code = update_profile(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            nickname=nickname,
            avatar_path=avatar_path,
        )

        return JsonResponse(response, status=status_code)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


@csrf_protect
@login_required
def delete(request):
    """
    Delete the profile of the logged-in user.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: A success message or an error message.
    """
    # Enforce the POST method
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method, only POST is allowed"}, status=405)

    try:
        user_id = request.user.id
        response, status_code = delete_profile(user_id=user_id)
        return JsonResponse(response, status=status_code)
    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


def action(request):
    data = {'message': 'OK'}
    return JsonResponse(data, status=200)
