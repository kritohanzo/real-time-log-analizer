from django.core.management.base import BaseCommand

from logs.models import LogType, SearchPattern


class Command(BaseCommand):
    help = "create default log types"
    default_log_types = [
        {"name": "HTTP"},
        {"name": "FTP"},
        {"name": "DNS"},
        {"name": "SMTP"},
        {"name": "POP"},
        {"name": "FIREWALL"},
    ]

    def handle(self, *args, **options):
        print("START CREATION DEFAULT LOG TYPES:", end=" ")
        log_types_exists = LogType.objects.filter(
            name__in=[log_type.get("name") for log_type in self.default_log_types]
        ).exists()
        if not log_types_exists:
            log_types = LogType.objects.bulk_create(
                [LogType(**fields) for fields in self.default_log_types]
            )
            for log_type in log_types:
                log_type.search_patterns.set(
                    SearchPattern.objects.filter(name__startswith=log_type.name)
                )
                log_type.save()
            print("CREATED")
        else:
            print("ALREADY EXISTS")
