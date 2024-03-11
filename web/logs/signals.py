from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from logs.models import AnomalousLogEvent

@receiver(post_save, sender=AnomalousLogEvent)
def notify_users(sender, instance, *args, **kwargs):
    channel_layer = get_channel_layer()
    # print(instance.datetime)
    message = f"[{instance.datetime}] {instance.text}"
    async_to_sync(channel_layer.group_send)("logs", message={
    "type": "websocket.broadcast",
    "message": message
    })