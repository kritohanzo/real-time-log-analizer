from django.core.management.base import BaseCommand, CommandError
from users.models import User
from dotenv import load_dotenv
import os


load_dotenv(override=True)


class Command(BaseCommand):
    help = "create deafult superuser"

    def handle(self, *args, **options):
        username = os.getenv("DEFAULT_SUPERUSER_USERNAME", "root")
        password = os.getenv("DEFAULT_SUPERUSER_PASSWORD", "root")
        User.objects.create_superuser(username=username, password=password)