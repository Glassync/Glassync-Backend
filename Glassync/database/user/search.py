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


def find_users(searcher_id: int, request_string: str, relationship_filter: str = "all"):
    """
    Find up to 50 users by their first name, last name, or a combination of both.
    Optionally filter the results based on the relationship status.

    Args:
        searcher_id (int): The ID of the user performing the search.
        request_string (str): The search string, which may include a first name, last name, or both.
        relationship_filter (str): Filter results by relationship status.
                                   Options: "friends", "friend_request_sent", "friend_request_received",
                                            "not_friends", "all".

    Returns:
        tuple: A tuple containing a list of matching users (as dictionaries) and the HTTP status code.
    """
    try:
        # Split the request string by spaces
        search_terms = request_string.split()

        # Start building the query
        query = Q()

        # If there are two terms, assume first name and last name
        if len(search_terms) == 2:
            first_name, last_name = search_terms
            query |= Q(first_name__icontains=first_name, last_name__icontains=last_name)
        elif len(search_terms) == 1:
            # Single term could match either first name or last name
            term = search_terms[0]
            query |= Q(first_name__icontains=term) | Q(last_name__icontains=term)
        else:
            # Invalid or empty search string
            return {"error": "Invalid search string"}, 400

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
