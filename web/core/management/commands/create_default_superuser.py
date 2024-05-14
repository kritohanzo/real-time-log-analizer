from django.core.management.base import BaseCommand, CommandError
from users.models import User
from dotenv import load_dotenv
import os


load_dotenv(override=True)


class Command(BaseCommand):
    help = "create deafult superuser"

    def handle(self, *args, **options):
        print("START CREATION DEFAULT SUPERUSER:", end=" ")
        username = os.getenv("DEFAULT_SUPERUSER_USERNAME", "root")
        password = os.getenv("DEFAULT_SUPERUSER_PASSWORD", "root")
        user_exists = User.objects.filter(username=username).exists()
        if not user_exists:
            User.objects.create_superuser(username=username, password=password)
            print("CREATED")
        else:
            print('ALREADY EXISTS')