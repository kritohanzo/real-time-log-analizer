from django.core.management.base import BaseCommand, CommandError
from users.models import User


class Command(BaseCommand):
    help = "Create superuser"

    def add_arguments(self, parser):
        parser.add_argument("-u", "--username")
        parser.add_argument("-p", "--password")

    def handle(self, *args, **options):
        User.objects.create_superuser(
            username=options.get("username"),
            password=options.get("password")
        )