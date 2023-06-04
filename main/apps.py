from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        # Import the notify_handler function here
        from main.notify_handler import notify_handler
        from notifications.signals import notify

        # Connect the notify_handler function to the notify signal
        notify.connect(notify_handler)