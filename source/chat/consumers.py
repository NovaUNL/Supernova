import asyncio
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from chat import models as chat


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.rooms = dict()
        self.lock = asyncio.Lock()

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        async with self.lock:
            for room_identifier in self.rooms.keys():
                room_group_name = 'room_%s' % room_identifier
                # Leave room group
                await self.channel_layer.group_discard(
                    room_group_name,
                    self.channel_name)
                print(f"Disconnected {self.channel_name}")

    # Receive message from WebSocket
    async def receive(self, text_data):
        request_data = json.loads(text_data)
        if not isinstance(request_data, list):
            await self.send(text_data=json.dumps({
                "error": "Invalid message format",
            }))
            return

        for action in request_data:
            if 'type' not in action:
                await self.send(text_data=json.dumps({
                    "error": f"Invalid message format: {action}",
                }))
                return
            type = action['type']
            if type == 'room_send':
                if 'room' in action and 'message' in action:
                    room_identifier = action['room']
                    room_group_name = 'room_%s' % room_identifier
                    async with self.lock:
                        if room_identifier not in self.rooms:
                            self.rooms[room_identifier] = await self.get_room(room_identifier)
                            # Join room group
                            await self.channel_layer.group_add(
                                room_group_name,
                                self.channel_name)
                            print(f"Joined {room_group_name} - {room_identifier}")
                        room = self.rooms[room_identifier]
                    await self.channel_layer.group_send(
                        room_group_name,
                        {
                            'type': 'chat.message',
                            'message': await self.store_message(action['message'], room)
                        }
                    )
                    print(f"Broadcasted")

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def get_room(self, room_name):
        return chat.PublicRoom.objects.get(identifier=room_name)

    @database_sync_to_async
    def store_message(self, message, conversation):
        return message_serialize(
            chat.Message.objects.create(
                author=self.user,
                content=message,
                creation=timezone.now(),
                conversation=conversation))


def message_serialize(message):
    return {
        'id': message.id,
        'content': message.content,
        'author': {
            'id': message.author.id,
            'nickname': message.author.nickname,
            'pic': message.author.picture_thumbnail.url if message.author.picture else None,
            'url': message.author.get_absolute_url() if not message.author.is_anonymous else None,
        },
        'timestamp': message.creation.timestamp(),
        'datetime': message.creation.strftime('%y/%m/%d %H:%M')
    }
