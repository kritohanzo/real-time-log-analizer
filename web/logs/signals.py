from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from logs.models import AnomalousEvent
import json
import datetime
from zoneinfo import ZoneInfo
from qsstats import QuerySetStats

@receiver(signal=post_save, sender=AnomalousEvent)
def notify_users(sender, instance, *args, **kwargs):
    """Оповещает пользователей об аномальном событии.
    
    Используя вебсокет, генерирует сообщение об аномальном событии,
    рассылая его всем пользователям, которые в данный момент
    находятся на странице /logs/.
    """
    message = {
        "id": instance.id,
        "text": instance.text,
        "fact_datetime": str(instance.fact_datetime),
        "detected_datetime": str(instance.detected_datetime),
        "log_file": {
            "id": instance.log_file.id,
            "name": instance.log_file.name
        },
        "new_log_metric": [
            [str(instance.detected_datetime.astimezone(tz=ZoneInfo(key='Asia/Yekaterinburg')).replace(second=0, microsecond=0)), 1]
        ]
    }
    message = json.dumps(message)

    # message_datetime = instance.fact_datetime or instance.detected_datetime
    # message = f"[{instance.log_file.name} | {message_datetime}] {instance.text}"
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "logs",
        message={
            "type": "websocket.broadcast",
            "message": message
        }
    )