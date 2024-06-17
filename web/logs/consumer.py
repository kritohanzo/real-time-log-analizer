from channels.generic.websocket import AsyncWebsocketConsumer


class LogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("connected")
        await self.channel_layer.group_add("logs", self.channel_name)
        print(f"added {self.channel_name}")

    async def disconnect(self, code):
        print("disconnected")
        await self.channel_layer.group_discard("logs", self.channel_name)
        print(f"removed {self.channel_name}")

    async def websocket_broadcast(self, event):
        print("try to send broadcast message")
        await self.send(event.get("message"))
        print("sended broadcast message")
