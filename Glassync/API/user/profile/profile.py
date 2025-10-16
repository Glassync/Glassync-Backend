from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from Glassync.database.user.services import get_profile, update_profile, delete_profile
import json


@csrf_protect
@login_required
def get(request):
    """
    Retrieve the profile of a user via POST request.

    Args:
        request: The HTTP request object containing the logged-in user's info and the target user_id in the body.

    Returns:
        JsonResponse: The user's profile or an error message.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method, only POST is allowed"}, status=405)

    try:
        # Parse the JSON body to get the target user_id
        body = json.loads(request.body)
        user_id = body.get("user_id")

        # Ensure 'user_id' is provided
        if not user_id:
            return JsonResponse({"error": "Missing 'user_id' in request body"}, status=400)

        # Use the logged-in user's ID as `own_uid`
        own_uid = request.user.id

        # Retrieve the profile using the `get_profile` function
        profile, status_code = get_profile(own_uid=own_uid, user_id=user_id)

        # Return the response as JSON
        return JsonResponse(profile, status=status_code)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    except ValueError:
        return JsonResponse({"error": "'user_id' must be a valid integer"}, status=400)
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