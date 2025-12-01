from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, MessageHistory, Notification

@receiver(pre_save, sender=Message)
def save_old_message_content(sender, instance, **kwargs):
    """
    Before saving an edited message, store its previous content in MessageHistory.
    """
    if not instance.pk:
        # New message → no history needed
        return

    try:
        old_msg = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return

    # If content changed → log history
    if old_msg.content != instance.content:
        MessageHistory.objects.create(
            message=instance,
            old_content=old_msg.content
        )
        instance.edited = True

@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    """
    Create a notification for the receiver when a new message is created.
    """
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            content=f"New message from {instance.sender.username}"
        )


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Delete all messages, notifications and message histories
    when a user is deleted.
    """

    # Delete messages SENT by the user
    Message.objects.filter(sender=instance).delete()

    # Delete messages RECEIVED by the user
    Message.objects.filter(receiver=instance).delete()

    # Delete message history linked to those messages
    MessageHistory.objects.filter(message__sender=instance).delete()
    MessageHistory.objects.filter(message__receiver=instance).delete()

    # Delete user's notifications
    Notification.objects.filter(user=instance).delete()
