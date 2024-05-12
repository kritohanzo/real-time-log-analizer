import os
from celery import Celery
from datetime import timedelta
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check_log_files_every_5_sec': {
        'task': 'logs.tasks.read_log_files_task',
        'schedule': timedelta(seconds=5)
    }
}