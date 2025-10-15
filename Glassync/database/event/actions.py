from django.core.exceptions import ObjectDoesNotExist
from Glassync.models import Event, EventMember
from Glassync.database.friendship.services import are_friends


def invite_to_group_event(user_owner, user_id, event_id):
    """
    Invites a user to a group event.

    Args:
        user_owner (int): The ID of the user inviting another user to the event.
        user_id (int): The ID of the user being invited.
        event_id (int): The ID of the event.

    Returns:
        dict: A dictionary with the result of the operation.
              Example:
              - Success: {'message': 'Invitation sent successfully', 'status': 201}
              - Error: {'error': 'Users are not friends', 'status': 403}
              - Error: {'error': 'User is already invited', 'status': 400}
    """
    try:
        # Check if the two users are friends
        if not are_friends(user_owner, user_id):
            return {'error': 'Users are not friends', 'status': 403}

        # Ensure the user is not already invited
        if EventMember.objects.filter(id_event_id=event_id, id_user_id=user_id).exists():
            return {'error': 'User is already invited', 'status': 400}

        # Add the invitation
        EventMember.objects.create(id_event_id=event_id, id_user_id=user_id, accept_invitation=False)
        return {'message': 'Invitation sent successfully', 'status': 201}

    except ObjectDoesNotExist:
        return {'error': 'Event or user does not exist', 'status': 404}


def accept_group_event_invite(user_id, event_id):
    """
    Accepts a group event invitation.

    Args:
        user_id (int): The ID of the user accepting the invitation.
        event_id (int): The ID of the event.

    Returns:
        dict: A dictionary with the result of the operation.
              Example:
              - Success: {'message': 'Invitation accepted', 'status': 200}
              - Error: {'error': 'Invitation not found or already accepted', 'status': 400}
    """
    try:
        # Find the invitation
        event_member = EventMember.objects.get(id_event_id=event_id, id_user_id=user_id, accept_invitation=False)

        # Accept the invitation
        event_member.accept_invitation = True
        event_member.save()
        return {'message': 'Invitation accepted', 'status': 200}

    except ObjectDoesNotExist:
        return {'error': 'Invitation not found or already accepted', 'status': 400}


def decline_group_event_invite(user_id, event_id):
    """
    Declines a group event invitation.

    Args:
        user_id (int): The ID of the user declining the invitation.
        event_id (int): The ID of the event.

    Returns:
        dict: A dictionary with the result of the operation.
              Example:
              - Success: {'message': 'Invitation declined', 'status': 200}
              - Error: {'error': 'Invitation not found or already accepted', 'status': 400}
    """
    try:
        # Find the invitation
        event_member = EventMember.objects.get(id_event_id=event_id, id_user_id=user_id, accept_invitation=False)

        # Delete the invitation
        event_member.delete()
        return {'message': 'Invitation declined', 'status': 200}

    except ObjectDoesNotExist:
        return {'error': 'Invitation not found or already accepted', 'status': 400}


def quit_group_event(user_id, event_id):
    """
    Allows a user to quit a group event.

    Args:
        user_id (int): The ID of the user quitting the event.
        event_id (int): The ID of the event.

    Returns:
        dict: A dictionary with the result of the operation.
              Example:
              - Success: {'message': 'User has left the event', 'status': 200}
              - Error: {'error': 'Event creator cannot leave their own event', 'status': 403}
              - Error: {'error': 'User is not part of the event', 'status': 400}
    """
    try:
        # Check if the user is the event creator
        event = Event.objects.get(id=event_id)
        if event.creator_id == user_id:
            return {'error': 'Event creator cannot leave their own event', 'status': 403}

        # Find the membership row
        event_member = EventMember.objects.get(id_event_id=event_id, id_user_id=user_id, accept_invitation=True)

        # Delete the membership
        event_member.delete()
        return {'message': 'User has left the event', 'status': 200}

    except ObjectDoesNotExist:
        return {'error': 'User is not part of the event', 'status': 400}