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
    Retrieve the profile of a user or search for users based on filters via POST request.

    Args:
        request: The HTTP request object containing the logged-in user's info and filter parameters in the body.

    Returns:
        JsonResponse: The user's profile, a list of users, or an error message.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method, only POST is allowed"}, status=405)

    try:
        # Parse the JSON body
        body = json.loads(request.body)

        # Check if 'user_id' is provided
        user_id = body.get("user_id")

        if user_id:
            # If 'user_id' is present, use get_profile to retrieve the user's profile
            own_uid = request.user.id
            profile, status_code = get_profile(own_uid=own_uid, user_id=user_id)
            return JsonResponse(profile, status=status_code)
        else:
            # If no 'user_id', handle search filters
            request_string = body.get("search_string", "")
            request_filter = body.get("request_filter", "all")  # Default to "all"
            relationship_filter = body.get("relationship_filter", "all")  # Default to "all"

            # Validate that a search string is provided
            if not request_string:
                return JsonResponse({"error": "Missing 'search_string' in request body"}, status=400)

            # Retrieve matching users
            searcher_id = request.user.id
            users, status_code = find_users(
                searcher_id=searcher_id,
                request_string=request_string,
                relationship_filter=relationship_filter,
                request_filter=request_filter
            )
            return JsonResponse({"users": users}, status=status_code)

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
