from django.core.management.base import BaseCommand, CommandError
from logs.models import NotificationType


class Command(BaseCommand):
    help = "create default notification types"
    default_notification_types = [
        {"method": "websocket", "description": "Оповещение на странице"},
        {"method": "email", "description": "Письмо на почту"},
        {"method": "sms", "description": "SMS сообщение на телефон"},
        {"method": "call", "description": "Звонок на телефон"},
    ]

    def handle(self, *args, **options):
        print("START CREATION DEFAULT NOTIFICATION TYPES:", end=" ")
        notification_types_exists = NotificationType.objects.filter(
            method__in=[notification_type.get("method") for notification_type in self.default_notification_types]
        ).exists()
        if not notification_types_exists:
            NotificationType.objects.bulk_create([NotificationType(**fields) for fields in self.default_notification_types])
            print("CREATED")
        else:
            print("ALREADY EXISTS")