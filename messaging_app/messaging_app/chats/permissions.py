from rest_framework import permissions

class IsParticipantOrOwner(permissions.BasePermission):
    """
    Object-level permission to allow only participants (or owner/sender/recipient)
    of a message or conversation to access it.

    Works with objects that expose one of:
    - a `participants` attribute (ManyToMany or iterable)
    - `sender`, `recipient`, `user`, or `owner` attribute(s)

    Usage:
    - Add to a viewset via permission_classes = [IsAuthenticated, IsParticipantOrOwner]
    - Ensure the viewset's list queryset is filtered to the current user so listing endpoints only show their own objects.
    """

    def has_permission(self, request, view):
        # Require authentication for all actions
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # If object exposes participants (ManyToMany manager or iterable)
        participants = getattr(obj, "participants", None)
        if participants is not None:
            # Try Django manager (.all())
            try:
                return user in participants.all()
            except Exception:
                # Fallback to iterable membership
                try:
                    return user in participants
                except Exception:
                    pass

        # Fallback: check common owner-like fields
        for attr in ("sender", "recipient", "user", "owner"):
            owner = getattr(obj, attr, None)
            if owner is not None:
                try:
                    return user == owner
                except Exception:
                    pass

        # Deny by default
        return False