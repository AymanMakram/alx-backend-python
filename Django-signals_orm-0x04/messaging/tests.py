from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification


class NotificationSignalTest(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(username="sender", password="1234")
        self.receiver = User.objects.create_user(username="receiver", password="1234")

    def test_notification_created(self):
        msg = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello!"
        )

        self.assertEqual(Notification.objects.count(), 1)

        notif = Notification.objects.first()
        self.assertEqual(notif.user, self.receiver)
        self.assertEqual(notif.message, msg)
