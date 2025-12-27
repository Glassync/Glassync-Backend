from Glassync.database.notification.services import create_notification, delete_notification
from Glassync.models import UsersRelationship
from django.core.exceptions import ObjectDoesNotExist
from Glassync.API.errors import ERRORS


def get_relationship_row(user1, user2):
    try:
        relationship = UsersRelationship.objects.get(
            id_user1=user1,
            id_user2=user2
        )
        return relationship, relationship.status_user1, relationship.status_user2
    except ObjectDoesNotExist:
        try:
            relationship = UsersRelationship.objects.get(
                id_user1=user2,
                id_user2=user1
            )
            return relationship, relationship.status_user2, relationship.status_user1
        except ObjectDoesNotExist:
            return None, None, None

def check_status(user1, user2):
    relationship, user1_status, user2_status = get_relationship_row(user1, user2)
    if relationship:
        if user1_status is True and user2_status is True:
            return "friends"
        elif user1_status is True and user2_status is False:
            return "friend_request_sent"
        elif user1_status is False and user2_status is True:
            return "friend_request_received"
    relationship, user2_status, user1_status = get_relationship_row(user2, user1)
    if relationship:
        if user2_status is True and user1_status is True:
            return "friends"
        elif user2_status is True and user1_status is False:
            return "friend_request_received"
        elif user2_status is False and user1_status is True:
            return "friend_request_sent"
    return "not_friends"


def are_friends(user1, user2):
    return check_status(user1, user2) == "friends"


def accept_friendship(user_sender, user_accepted):
    status = check_status(user_sender, user_accepted)
    if status == "friend_request_sent":
        relationship, _, _ = get_relationship_row(user_sender, user_accepted)
        relationship.status_user2 = True
        relationship.save()
        delete_notification(id_user=user_accepted.id, id_user_sender=user_sender.id)
        return {'message': 'Friendship request accepted', 'status': 200}
    return {'errors': [ERRORS["friendship"]["no_request_found"]], 'status': 400}


def decline_friendship(user_sender, user_declined):
    status = check_status(user_sender, user_declined)
    if status == "friend_request_sent":
        relationship, _, _ = get_relationship_row(user_sender, user_declined)
        relationship.delete()
        delete_notification(id_user=user_declined.id, id_user_sender=user_sender.id)
        return {'message': 'Friendship request declined', 'status': 200}
    return {'errors': [ERRORS["friendship"]["no_request_found"]], 'status': 400}


def request_friendship(user_sender, user_receiver):
    if user_sender == user_receiver:
        return {'errors': [ERRORS["friendship"]["cannot_friend_self"]], 'status': 400}
    status = check_status(user_sender, user_receiver)
    if status == "not_friends":
        UsersRelationship.objects.create(
            id_user1=user_sender,
            id_user2=user_receiver,
            status_user1=True,
            status_user2=False
        )
        create_notification(id_user_sender=user_sender.id, id_user=user_receiver.id)
        return {'message': 'Friendship request sent', 'status': 201}
    return {'errors': [ERRORS["friendship"]["could_not_create"]], 'status': 400}


def cancel_friendship_request(user_sender, user_receiver):
    status = check_status(user_sender, user_receiver)
    if status == "friend_request_sent":
        relationship, _, _ = get_relationship_row(user_sender, user_receiver)
        relationship.delete()
        delete_notification(id_user=user_receiver.id, id_user_sender=user_sender.id)
        return {'message': 'Friendship request canceled', 'status': 200}
    return {'errors': [ERRORS["friendship"]["no_request_found"]], 'status': 400}


def delete_friendship(user_sender, user_receiver):
    status = check_status(user_sender, user_receiver)
    if status == "friends":
        relationship, _, _ = get_relationship_row(user_sender, user_receiver)
        if relationship is None:
            return {'errors': [ERRORS["friendship"]["no_friendship_found"]], 'status': 400}
        relationship.delete()
        return {'message': 'Friendship deleted', 'status': 200}
    return {'errors': [ERRORS["friendship"]["no_friendship_found"]], 'status': 400}
