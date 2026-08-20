from django.apps import AppConfig


class QueueConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.queue"
    label = "queue"
    verbose_name = "Queue"
