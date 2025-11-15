import json
import re
from typing import List

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.contrib.auth import get_user_model

from Glassync.API.errors import ERRORS

User = get_user_model()


def json_response(data, status=200):
    return JsonResponse(
        data,
        status=status,
        content_type="application/json"
    )


@csrf_exempt
@require_POST
def signup(request: HttpRequest):
    """
    Register a new user.
    Expects: email, password, first_name, last_name (optionally: nickname, avatar_path)
    """
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        nickname = data.get("nickname")
        avatar_path = data.get("avatar_path")

        errors = collect_field_errors_signup(email, password, first_name, last_name)
        if User.objects.filter(email=email).exists():
            errors.append(ERRORS["auth"]["user_exists"])

        if errors:
            return json_response({"errors": errors}, status=400)

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            nickname=nickname,
            avatar_path=avatar_path
        )
        return json_response({"message": "User created successfully"}, status=201)
    except json.JSONDecodeError:
        return json_response({"errors": [ERRORS["general"]["invalid_json"]]}, status=400)
    except Exception as e:
        return json_response({
            "errors": [dict(ERRORS["general"]["unexpected_error"], details=str(e))]
        }, status=500)


@csrf_exempt
@require_POST
def login(request: HttpRequest):
    """
    Log in a user.
    Expects: email, password
    """
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        errors = collect_field_errors_login(email, password)
        if errors:
            return json_response({"errors": errors}, status=400)

        user = authenticate(request, email=email, password=password)
        if user is not None:
            dj_login(request, user)
            return json_response({"message": "Logged in successfully"})
        else:
            return json_response({"errors": [ERRORS["auth"]["invalid_credentials"]]}, status=401)
    except json.JSONDecodeError:
        return json_response({"errors": [ERRORS["general"]["invalid_json"]]}, status=400)
    except Exception as e:
        return json_response({
            "errors": [dict(ERRORS["general"]["unexpected_error"], details=str(e))]
        }, status=500)


@csrf_exempt
@require_POST
def logout(request: HttpRequest):
    """
    Log out the current user.
    """
    try:
        if request.user.is_authenticated:
            dj_logout(request)
            return json_response({"message": "Logged out successfully"})
        else:
            return json_response({"errors": [ERRORS["auth"]["not_logged_in"]]}, status=401)
    except Exception as e:
        return json_response({
            "errors": [dict(ERRORS["general"]["unexpected_error"], details=str(e))]
        }, status=500)


def is_valid_name(name: str) -> bool:
    """Allows letters, spaces, hyphens, apostrophes (adjust as needed)"""
    return bool(re.fullmatch(r"[A-Za-zÀ-ÿА-ЯЁа-яё '-]{1,50}", name.strip()))


def collect_field_errors_signup(
    email: str,
    password: str,
    first_name: str,
    last_name: str
) -> List[dict]:
    errors = []
    if not email:
        errors.append(ERRORS["fields"]["missing_email"])
    if not password:
        errors.append(ERRORS["fields"]["missing_password"])
    if not first_name:
        errors.append(ERRORS["fields"]["missing_first_name"])
    elif not is_valid_name(first_name):
        errors.append(ERRORS["fields"]["invalid_first_name"])
    if not last_name:
        errors.append(ERRORS["fields"]["missing_last_name"])
    elif not is_valid_name(last_name):
        errors.append(ERRORS["fields"]["invalid_last_name"])
    return errors


def collect_field_errors_login(
    email: str,
    password: str
) -> List[dict]:
    errors = []
    if not email:
        errors.append(ERRORS["fields"]["missing_email"])
    if not password:
        errors.append(ERRORS["fields"]["missing_password"])
    return errors