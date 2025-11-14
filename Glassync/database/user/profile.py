from Glassync.database.friendship.services import are_friends
from Glassync.models import User
from django.core.exceptions import ObjectDoesNotExist
from Glassync.API.errors import ERRORS


def get_profile(own_uid: int, user_id: int):
    """
    Retrieve the profile data of a user.

    Args:
        own_uid (int): The ID of the requesting user.
        user_id (int): The ID of the user whose profile is being requested.

    Returns:
        tuple: A tuple containing the profile as a dictionary and the HTTP status code.
    """
    try:
        # Uncomment and use this block if you want to restrict profile viewing to self/friends only
        # if own_uid != user_id and not are_friends(own_uid, user_id):
        #     return {"errors": [ERRORS["user"]["permission_denied"]]}, 403

        user = User.objects.get(id=user_id)
        profile_data = {
            "id": user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "nickname": user.nickname,
            "avatar_path": user.avatar_path,
        }
        return profile_data, 200

    except ObjectDoesNotExist:
        return {"errors": [ERRORS["user"]["not_found"]]}, 404
    except Exception as e:
        return {"errors": [dict(ERRORS["general"]["unexpected_error"], details=str(e))]}, 500


def update_profile(user_id: int, first_name=None, last_name=None, nickname=None, avatar_path=None, password=None, current_password=None):
    """
    Update the profile data of a user, possibly including password change.
    """
    try:
        user = User.objects.get(id=user_id)

        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if nickname is not None:
            user.nickname = nickname
        if avatar_path is not None:
            user.avatar_path = avatar_path

        if password is not None:
            if current_password is None or not user.check_password(current_password):
                return {"errors": [ERRORS["user"]["current_password_incorrect"]]}, 403
            user.set_password(password)

        user.save()
        return {"message": "Profile updated successfully"}, 200
    except ObjectDoesNotExist:
        return {"errors": [ERRORS["user"]["not_found"]]}, 404
    except Exception as e:
        return {"errors": [dict(ERRORS["general"]["unexpected_error"], details=str(e))]}, 500


def delete_profile(user_id: int):
    """
    Delete the profile of a user.

    Args:
        user_id (int): The ID of the user to delete.

    Returns:
        tuple: A tuple containing a success message or an error message and the HTTP status code.
    """
    try:
        user = User.objects.get(id=user_id)
        user.delete()  # Delete the user from the database
        return {"message": "Profile deleted successfully"}, 200
    except ObjectDoesNotExist:
        return {"errors": [ERRORS["user"]["not_found"]]}, 404
    except Exception as e:
        return {"errors": [dict(ERRORS["general"]["unexpected_error"], details=str(e))]}, 500
