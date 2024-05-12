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
        notification_types = [NotificationType(**fields) for fields in self.default_notification_types]
        NotificationType.objects.bulk_create(notification_types)