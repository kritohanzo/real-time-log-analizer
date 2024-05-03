from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from logs.models import AnomalousEvent

@receiver(signal=post_save, sender=AnomalousEvent)
def notify_users(sender, instance, *args, **kwargs):
    """Оповещает пользователей об аномальном событии.
    
    Используя вебсокет, генерирует сообщение об аномальном событии,
    рассылая его всем пользователям, которые в данный момент
    находятся на странице /logs/.
    """
    message = f"[{instance.log_file.name} | {instance.datetime}] {instance.text}"
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "logs",
        message={
            "type": "websocket.broadcast",
            "message": message
        }
    )