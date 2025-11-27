from django.db import models

class UnreadMessagesManager(models.Manager):
    """
    Custom manager to return unread messages for a specific user.
    """

    def unread_for_user(self, user):
        return (
            super()
            .get_queryset()
            .filter(receiver=user, read=False)
            .only("id", "sender", "content", "timestamp")  # required optimization
        )
