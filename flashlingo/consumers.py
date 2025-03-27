import json
from typing import List

from channels.generic.websocket import AsyncWebsocketConsumer


class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({"message": "connected"}))

    async def disconnect(self, code):
        return super().disconnect(code)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        time = data["time"]
        user_input = data["input"]
        translations: List[str] = data["translations"]
        is_correct = user_input in translations
        points = 0
        if not is_correct or time > 10:
            points = -1
        elif is_correct and time <= 4:
            points = 1
        await self.send(text_data=json.dumps({"points": points}))
