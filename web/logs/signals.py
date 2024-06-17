import json
from zoneinfo import ZoneInfo

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.db.models.signals import post_save
from django.dispatch import receiver

from logs.models import AnomalousEvent


@receiver(signal=post_save, sender=AnomalousEvent)
def notify_users(sender, instance, *args, **kwargs):
    """Оповещает пользователей об аномальном событии.

    Используя вебсокет, генерирует сообщение об аномальном событии,
    рассылая его всем пользователям, которые в данный момент
    находятся на странице /logs/, в том случае, если аномальное событие
    не пренадлежит файлу для одноразового сканирования.
    """
    if instance.log_file.one_time_scan or not instance.count_of_events is None:
        return

    message = {
        "id": instance.id,
        "text": instance.text,
        "fact_datetime": str(instance.fact_datetime),
        "detected_datetime": str(instance.detected_datetime),
        "log_file": {"id": instance.log_file.id, "name": instance.log_file.name},
        "detected_search_pattern": {
            "id": instance.detected_search_pattern.id,
            "name": instance.detected_search_pattern.name,
        },
        "new_log_metric": [
            [
                str(
                    instance.detected_datetime.astimezone(
                        tz=ZoneInfo(key="Asia/Yekaterinburg")
                    ).replace(second=0, microsecond=0)
                ),
                1,
            ]
        ],
    }
    message = json.dumps(message)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "logs", message={"type": "websocket.broadcast", "message": message}
    )
