from django.apps import AppConfig


class ChatsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chats"  # <- ensure this is the full import path to the app package
    verbose_name = "Chats"