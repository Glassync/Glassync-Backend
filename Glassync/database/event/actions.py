from django.core.exceptions import ObjectDoesNotExist

from Glassync.database.notification.services import set_event_notification_interval
from Glassync.models import Event, EventMember
from Glassync.database.friendship.services import are_friends
from Glassync.API.errors import ERRORS


def invite_to_group_event(user_owner, user_id, event_id):
    """
    Invites a user to a group event.
    Returns a dict with either 'message' and 'status',
    or 'errors' (list) and 'status'.
    """
    try:
        # Check if the event exists and user_owner is the creator
        event = Event.objects.get(id=event_id)
        if event.creator_id != user_owner:
            return {
                'errors': [ERRORS["event"]["permission_denied"]],
                'status': 403
            }

        # Check if the two users are friends
        if not are_friends(user_owner, user_id):
            return {
                'errors': [ERRORS["event"]["invite_not_friends"]],
                'status': 403
            }

        # Ensure the user is not already invited
        if EventMember.objects.filter(id_event_id=event_id, id_user_id=user_id).exists():
            return {
                'errors': [ERRORS["event"]["already_invited"]],
                'status': 400
            }

        # Add the invitation
        EventMember.objects.create(id_event_id=event_id, id_user_id=user_id, accept_invitation=False)
        return {'message': 'Invitation sent successfully', 'status': 201}

    except Event.DoesNotExist:
        return {
            'errors': [ERRORS["event"]["event_not_found"]],
            'status': 404
        }


def accept_group_event_invite(user_id, event_id, notifications=None):
    """
    Accepts a group event invitation.
    """
    try:
        event_member = EventMember.objects.get(id_event_id=event_id, id_user_id=user_id, accept_invitation=False)
        event_member.accept_invitation = True
        event_member.save()

        # Handle notifications
        if notifications is not None:
            # If you only allow one notification interval per event/user, pick the first valid one
            for notif in notifications:
                try:
                    notif_int = int(notif)
                    if notif_int > 0:
                        set_event_notification_interval(event_id, user_id, notif_int)
                        break  # Only set once, break after the first valid
                except Exception:
                    return {
                        'errors': [ERRORS["general"]["unexpected_error"]],
                        'status': 400
                    }

        return {'message': 'Invitation accepted', 'status': 200}

    except ObjectDoesNotExist:
        return {
            'errors': [ERRORS["event"]["invitation_not_found"]],
            'status': 400
        }


def decline_group_event_invite(user_id, event_id):
    """
    Declines a group event invitation.
    """
    try:
        event_member = EventMember.objects.get(id_event_id=event_id, id_user_id=user_id, accept_invitation=False)
        event_member.delete()
        return {'message': 'Invitation declined', 'status': 200}

    except ObjectDoesNotExist:
        return {
            'errors': [ERRORS["event"]["invitation_not_found"]],
            'status': 400
        }


def quit_group_event(user_id, event_id):
    """
    Allows a user to quit a group event.
    """
    try:
        event = Event.objects.get(id=event_id)
        if event.creator_id == user_id:
            return {
                'errors': [ERRORS["event"]["creator_cannot_leave"]],
                'status': 403
            }

        event_member = EventMember.objects.get(id_event_id=event_id, id_user_id=user_id, accept_invitation=True)
        event_member.delete()
        return {'message': 'User has left the event', 'status': 200}

    except ObjectDoesNotExist:
        return {
            'errors': [ERRORS["event"]["user_not_in_event"]],
            'status': 400
        }
