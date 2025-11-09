import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.contrib.auth import get_user_model

User = get_user_model()


@csrf_protect
def signup(request):
    """
    Register a new user.
    Expects: email, password, first_name, last_name (optionally: nickname, avatar_path)
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method, only POST is allowed"}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        nickname = data.get("nickname")
        avatar_path = data.get("avatar_path")

        # Basic validation
        if not email or not password or not first_name or not last_name:
            return JsonResponse({"error": "Email, password, first_name, and last_name are required"}, status=400)
        if not is_valid_name(first_name) or not is_valid_name(last_name):
            return JsonResponse(
                {"error": "Names must only contain letters, hyphens, apostrophes, or spaces, and be 1-50 characters."},
                status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "A user with this email already exists"}, status=400)

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            nickname=nickname,
            avatar_path=avatar_path
        )
        return JsonResponse({"message": "User created successfully"}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


@csrf_protect
def login(request):
    """
    Log in a user.
    Expects: email, password
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method, only POST is allowed"}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        if not all([email, password]):
            return JsonResponse({"error": "Email and password are required"}, status=400)

        user = authenticate(request, email=email, password=password)
        if user is not None:
            dj_login(request, user)
            return JsonResponse({"message": "Logged in successfully"})
        else:
            return JsonResponse({"error": "Invalid email or password"}, status=401)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


@csrf_protect
def logout(request):
    """
    Log out the current user.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method, only POST is allowed"}, status=405)
    try:
        if request.user.is_authenticated:
            dj_logout(request)
            return JsonResponse({"message": "Logged out successfully"})
        else:
            return JsonResponse({"error": "User is not logged in"}, status=401)
    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


def is_valid_name(name):
    # Allows letters, spaces, hyphens, apostrophes (adjust as needed)
    return bool(re.fullmatch(r"[A-Za-zÀ-ÿА-ЯЁа-яё '-]{1,50}", name.strip()))
