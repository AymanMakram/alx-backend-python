from rest_framework import permissions
from django.shortcuts import get_object_or_404

from .models import Conversation, Message


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allow only authenticated users who are participants of a conversation
    to send, view, update and delete messages in that conversation.

    - has_permission: ensures request.user is authenticated and, for creates,
      that the supplied conversation id belongs to a conversation the user participates in.
    - has_object_permission: ensures request.user is a participant (or sender/owner)
      of the specific Conversation or Message object being accessed.
    """

    def has_permission(self, request, view):
        # Require authentication for all API access
        if not (request.user and request.user.is_authenticated):
            return False

        # For message creation (POST), ensure the user is a participant of the target conversation.
        # We try to detect creation on MessageViewSet by checking request.method and whether
        # 'conversation' is present in the incoming data.
        if request.method == "POST":
            # If the view uses `conversation` in URL (e.g. nested endpoint), view.kwargs may contain it.
            conversation_id = request.data.get("conversation") or request.query_params.get("conversation") or view.kwargs.get("pk") or view.kwargs.get("conversation_pk")
            if conversation_id:
                try:
                    conversation = get_object_or_404(Conversation, pk=conversation_id)
                except Exception:
                    return False
                # If user is in participants, allow creation
                try:
                    return request.user in conversation.participants.all()
                except Exception:
                    # Fallback membership check for non-manager iterables
                    return request.user in list(conversation.participants.all())
            # If no conversation supplied, deny — creation must target a conversation.
            return False

        # For non-POST, allow to proceed to object-level checks (if applicable)
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        # If the object is a Conversation: ensure user is a participant
        if isinstance(obj, Conversation):
            try:
                return user in obj.participants.all()
            except Exception:
                return user in list(obj.participants.all())

        # If the object is a Message: allow if the user is a participant in the message's conversation,
        # or the sender/recipient (covering models that store sender/recipient directly).
        if isinstance(obj, Message):
            # Prefer conversation participants check
            conv = getattr(obj, "conversation", None)
            if conv is not None:
                try:
                    return user in conv.participants.all()
                except Exception:
                    return user in list(conv.participants.all())

            # Fallback to sender/recipient/user/owner fields
            for attr in ("sender", "recipient", "user", "owner"):
                owner = getattr(obj, attr, None)
                if owner is not None:
                    if user == owner:
                        return True

        # Deny by default
        return False