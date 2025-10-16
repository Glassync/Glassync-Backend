from Glassync.models import User
from django.db.models import Q
from Glassync.database.friendship.services import are_friends, check_status
from django.core.exceptions import ObjectDoesNotExist


def get_friends(user_id: int):
    """
    Retrieve all friends of a specific user.

    Args:
        user_id (int): The ID of the user whose friends are being retrieved.

    Returns:
        tuple: A tuple containing a list of friends (as dictionaries) and the HTTP status code.
    """
    try:
        # Fetch the user
        user = User.objects.get(id=user_id)

        # Query all users and filter only friends
        all_users = User.objects.exclude(id=user_id)  # Exclude the user themselves
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
        return {"error": "User not found"}, 404
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}, 500


def find_users(
    searcher_id: int,
    request_string: str,
    relationship_filter: str = "all",
    request_filter: str = "all"
):
    """
    Find up to 50 users by their first name, last name, nickname, or email.
    Optionally filter the results based on relationship status.

    Args:
        searcher_id (int): The ID of the user performing the search.
        request_string (str): The search string to match users.
        relationship_filter (str): Filter results by relationship status.
                                   Options: "friends", "friend_request_sent",
                                            "friend_request_received", "not_friends", "all".
        request_filter (str): Specifies which fields to search on.
                              Options: "full_name", "nickname", "email", "all".

    Returns:
        tuple: A tuple containing a list of matching users (as dictionaries) and the HTTP status code.
    """
    try:
        # Validate request_filter
        valid_request_filters = {"full_name", "nickname", "email", "all"}
        if request_filter not in valid_request_filters:
            return {"error": f"Invalid request filter. Use one of {valid_request_filters}."}, 400

        # Validate relationship_filter
        valid_relationship_filters = {"friends", "friend_request_sent", "friend_request_received", "not_friends", "all"}
        if relationship_filter not in valid_relationship_filters:
            return {"error": f"Invalid relationship filter. Use one of {valid_relationship_filters}."}, 400

        # Build the search query based on request_filter
        query = Q()
        if request_filter == "full_name":
            # Split the request string to handle first name and last name
            search_terms = request_string.split()
            if len(search_terms) == 2:
                query |= Q(first_name__icontains=search_terms[0], last_name__icontains=search_terms[1])
            elif len(search_terms) == 1:
                query |= Q(first_name__icontains=request_string) | Q(last_name__icontains=request_string)
            else:
                return {"error": "Invalid search string for full name. Provide a first and/or last name."}, 400
        elif request_filter == "nickname":
            query |= Q(nickname__icontains=request_string)
        elif request_filter == "email":
            query |= Q(email__icontains=request_string)
        elif request_filter == "all":
            query |= Q(first_name__icontains=request_string) | Q(last_name__icontains=request_string)
            query |= Q(nickname__icontains=request_string) | Q(email__icontains=request_string)

        # Exclude the searcher themselves and apply the query
        matching_users = User.objects.filter(query).exclude(id=searcher_id)

        # Filter based on relationship status
        filtered_users = []
        for user in matching_users:
            status = check_status(searcher_id, user.id)

            if relationship_filter == "all" or status == relationship_filter:
                filtered_users.append({
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "nickname": user.nickname,
                    "avatar_path": user.avatar_path,
                    "relationship_status": status
                })

        # Limit results to 50 users
        filtered_users = filtered_users[:50]

        # Return the formatted results
        return filtered_users, 200

    except ObjectDoesNotExist:
        return {"error": "No users found matching the search criteria"}, 404
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}, 500
