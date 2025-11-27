from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Message, MessageHistory

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
