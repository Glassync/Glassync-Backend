from Glassync.database.friendship.services import are_friends
from Glassync.models import User
from django.core.exceptions import ObjectDoesNotExist


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
        # Check if the requested user is the same as the requesting user or if they are friends
        # if own_uid != user_id and not are_friends(own_uid, user_id):
        #     return {"error": "Permission denied. You can only view your own profile or your friends' profiles."}, 403

        # Fetch the user's profile
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
        return {"error": "User not found"}, 404
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}, 500


def update_profile(user_id: int, first_name=None, last_name=None, nickname=None, avatar_path=None):
    """
    Update the profile data of a user.

    Args:
        user_id (int): The ID of the user to update.
        first_name (str, optional): Updated first name of the user.
        last_name (str, optional): Updated last name of the user.
        nickname (str, optional): Updated nickname of the user.
        avatar_path (str, optional): Updated avatar path of the user.

    Returns:
        tuple: A tuple containing a success message or an error message and the HTTP status code.
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

        user.save()  # Save the changes to the database
        return {"message": "Profile updated successfully"}, 200
    except ObjectDoesNotExist:
        return {"error": "User not found"}, 404
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}, 500


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
        return {"error": "User not found"}, 404
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}, 500
