from Glassync.models import UsersRelationship
from django.core.exceptions import ObjectDoesNotExist


def get_relationship_row(user1, user2):
    """
    Retrieve the relationship row between two users and their statuses.

    Args:
        user1 (User): The first user.
        user2 (User): The second user.

    Returns:
        tuple: (relationship_row, user1_status, user2_status) or (None, None, None) if no valid row exists.
    """
    try:
        relationship = UsersRelationship.objects.get(
            id_user1=user1,
            id_user2=user2
        )
        return relationship, relationship.status_user1, relationship.status_user2
    except ObjectDoesNotExist:
        return None, None, None


def check_status(user1, user2):
    """
    Check the status of the relationship between two users.

    Args:
        user1 (User): The first user.
        user2 (User): The second user.

    Returns:
        str: One of "friends", "friend_request_sent", "friend_request_received", or "not_friends".
    """
    # First, check if user1 is id_user1 and user2 is id_user2
    relationship, user1_status, user2_status = get_relationship_row(user1, user2)

    if relationship:
        if user1_status is True and user2_status is True:
            return "friends"
        elif user1_status is True and user2_status is False:
            return "friend_request_sent"
        elif user1_status is False and user2_status is True:
            return "friend_request_received"

    # If not found, check if user1 is id_user2 and user2 is id_user1
    relationship, user2_status, user1_status = get_relationship_row(user2, user1)

    if relationship:
        if user2_status is True and user1_status is True:
            return "friends"
        elif user2_status is True and user1_status is False:
            return "friend_request_received"  # Reversed order
        elif user2_status is False and user1_status is True:
            return "friend_request_sent"  # Reversed order

    # If no relationship is found in either direction
    return "not_friends"


def are_friends(user1, user2):
    """
    Check if two users are friends.

    Args:
        user1 (User): The first user.
        user2 (User): The second user.

    Returns:
        bool: True if the users are friends, False otherwise.
    """
    return check_status(user1, user2) == "friends"


def accept_friendship(user_sender, user_accepted):
    """
    Accept a friendship request.

    Args:
        user_sender (User): The user who sent the request.
        user_accepted (User): The user who accepts the request.

    Returns:
        dict: A dictionary with the result of the operation.
              Example:
              - Success: {'message': 'Friendship request accepted', 'status': 200}
              - Error: {'error': 'No friendship request found', 'status': 400}
    """
    status = check_status(user_sender, user_accepted)

    if status == "friend_request_sent":
        relationship, _, _ = get_relationship_row(user_sender, user_accepted)
        relationship.status_user2 = True
        relationship.save()
        return {'message': 'Friendship request accepted', 'status': 200}

    return {'error': 'No friendship request found', 'status': 400}


def decline_friendship(user_sender, user_declined):
    """
    Decline a friendship request.

    Args:
        user_sender (User): The user who sent the request.
        user_declined (User): The user who declines the request.

    Returns:
        dict: A dictionary with the result of the operation.
              Example:
              - Success: {'message': 'Friendship request declined', 'status': 200}
              - Error: {'error': 'No friendship request found', 'status': 400}
    """
    status = check_status(user_sender, user_declined)

    if status == "friend_request_sent":
        relationship, _, _ = get_relationship_row(user_sender, user_declined)
        relationship.delete()
        return {'message': 'Friendship request declined', 'status': 200}

    return {'error': 'No friendship request found', 'status': 400}


def request_friendship(user_sender, user_receiver):
    """
    Request a friendship.

    Args:
        user_sender (User): The user sending the request.
        user_receiver (User): The user receiving the request.

    Returns:
        dict: A dictionary with the result of the operation.
              Example:
              - Success: {'message': 'Friendship request sent', 'status': 201}
              - Error: {'error': 'Friendship request could not be created', 'status': 400}
              - Error: {'error': 'Cannot send a friend request to yourself', 'status': 400}
    """
    # Prevent users from sending a friend request to themselves
    if user_sender == user_receiver:
        return {'error': 'Cannot send a friend request to yourself', 'status': 400}

    status = check_status(user_sender, user_receiver)

    if status == "not_friends":
        UsersRelationship.objects.create(
            id_user1=user_sender,
            id_user2=user_receiver,
            status_user1=True,
            status_user2=False
        )
        return {'message': 'Friendship request sent', 'status': 201}

    return {'error': 'Friendship request could not be created', 'status': 400}


def cancel_friendship_request(user_sender, user_receiver):
    """
    Cancel a friendship request.

    Args:
        user_sender (User): The user who sent the request.
        user_receiver (User): The user who received the request.

    Returns:
        dict: A dictionary with the result of the operation.
              Example:
              - Success: {'message': 'Friendship request canceled', 'status': 200}
              - Error: {'error': 'No friendship request found', 'status': 400}
    """
    status = check_status(user_sender, user_receiver)

    if status == "friend_request_sent":
        relationship, _, _ = get_relationship_row(user_sender, user_receiver)
        relationship.delete()
        return {'message': 'Friendship request canceled', 'status': 200}

    return {'error': 'No friendship request found', 'status': 400}


def delete_friendship(user_sender, user_receiver):
    """
    Delete a friendship.

    Args:
        user_sender (User): One of the users in the friendship.
        user_receiver (User): The other user in the friendship.

    Returns:
        dict: A dictionary with the result of the operation.
              Example:
              - Success: {'message': 'Friendship deleted', 'status': 200}
              - Error: {'error': 'No friendship found to delete', 'status': 400}
    """
    status = check_status(user_sender, user_receiver)

    if status == "friends":
        relationship, _, _ = get_relationship_row(user_sender, user_receiver)
        relationship.delete()
        return {'message': 'Friendship deleted', 'status': 200}

    return {'error': 'No friendship found to delete', 'status': 400}
