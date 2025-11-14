from Glassync.models import User
from django.db.models import Q
from Glassync.database.friendship.services import are_friends, check_status
from django.core.exceptions import ObjectDoesNotExist
from Glassync.API.errors import ERRORS

def get_friends(user_id: int):
    """
    Retrieve all friends of a specific user.
    """
    try:
        user = User.objects.get(id=user_id)
        all_users = User.objects.exclude(id=user_id)
        friends = []

        for other_user in all_users:
            if are_friends(user.id, other_user.id):
                friends.append({
                    "id": other_user.id,
                    "first_name": other_user.first_name,
                    "last_name": other_user.last_name,
                    "email": other_user.email,
                    "nickname": other_user.nickname,
                    "avatar_path": other_user.avatar_path,
                })

        return friends, 200

    except ObjectDoesNotExist:
        return {"errors": [ERRORS["user"]["not_found"]]}, 404
    except Exception as e:
        return {"errors": [dict(ERRORS["general"]["unexpected_error"], details=str(e))]}, 500


def find_users(
    searcher_id: int,
    request_string: str,
    relationship_filter: str = "all",
    request_filter: str = "all"
):
    """
    Find up to 50 users by their first name, last name, nickname, or email.
    Optionally filter the results based on relationship status.
    """
    try:
        valid_request_filters = {"full_name", "nickname", "email", "all"}
        if request_filter not in valid_request_filters:
            return {"errors": [ERRORS["user"]["invalid_request_filter"]]}, 400

        valid_relationship_filters = {"friends", "friend_request_sent", "friend_request_received", "not_friends", "all"}
        if relationship_filter not in valid_relationship_filters:
            return {"errors": [ERRORS["user"]["invalid_relationship_filter"]]}, 400

        query = Q()
        if request_filter == "full_name":
            search_terms = request_string.split()
            if len(search_terms) == 2:
                query |= Q(first_name__icontains=search_terms[0], last_name__icontains=search_terms[1])
            elif len(search_terms) == 1:
                query |= Q(first_name__icontains=request_string) | Q(last_name__icontains=request_string)
            else:
                return {"errors": [ERRORS["user"]["invalid_search_string_full_name"]]}, 400
        elif request_filter == "nickname":
            query |= Q(nickname__icontains=request_string)
        elif request_filter == "email":
            query |= Q(email__icontains=request_string)
        elif request_filter == "all":
            query |= Q(first_name__icontains=request_string) | Q(last_name__icontains=request_string)
            query |= Q(nickname__icontains=request_string) | Q(email__icontains=request_string)

        matching_users = User.objects.filter(query).exclude(id=searcher_id)

        users_dict = {}
        for user in matching_users:
            status = check_status(searcher_id, user.id)
            if relationship_filter == "all" or status == relationship_filter:
                users_dict[str(user.id)] = {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "nickname": user.nickname,
                    "avatar_path": user.avatar_path,
                    "relationship_status": status
                }

        return {"users": users_dict}, 200

    except ObjectDoesNotExist:
        return {"errors": [ERRORS["user"]["no_users_found"]]}, 404
    except Exception as e:
        return {"errors": [dict(ERRORS["general"]["unexpected_error"], details=str(e))]}, 500