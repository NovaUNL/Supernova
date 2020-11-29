import asyncio
import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from chat import models as chat

log = logging.getLogger()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.conversations = dict()
        self.lock = asyncio.Lock()

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        async with self.lock:
            for room_identifier in self.conversations.keys():
                room_group_name = 'conversation_%s' % room_identifier
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
                log.error(f'Received an action (by {self.user.nickname}) without a type: {action}')
                await self.send(text_data=json.dumps({
                    "error": f"Invalid message format: {action}",
                }))
                return
            action_type = action['type']
            if action_type == 'send':
                if not ('conversation' in action and 'message' in action):
                    log.error(f'Received an invalid send action (by {self.user.nickname}): {action}')
                    continue
                conversation_id = action['conversation']
                conversation_group_name = 'conversation_%s' % conversation_id
                async with self.lock:
                    if conversation_id in self.conversations:
                        conversation = self.conversations[conversation_id]
                    else:
                        conversation = None
                if conversation:
                    await self.channel_layer.group_send(
                        conversation_group_name,
                        {
                            'type': 'chat.message',
                            'message': await self.store_message(action['message'], conversation)
                        }
                    )
            elif action_type == 'join':
                if 'conversation' not in action:
                    log.error(f'Received a join action (by {self.user.nickname}) without a conversation: {action}')
                    continue
                conversation_id = action['conversation']
                conversation_group_name = 'conversation_%s' % conversation_id
                async with self.lock:
                    if conversation_id not in self.conversations:
                        self.conversations[conversation_id] = await self.get_conversation(conversation_id)
                        # Join conversation group
                        await self.channel_layer.group_add(
                            conversation_group_name,
                            self.channel_name)
                        log.info(f"{self.user.nickname} joined {conversation_group_name} - {conversation_id}")
                    else:
                        log.info(f"{self.user.nickname} join request to {conversation_group_name} ignored "
                                 "(duplicated join or no permissions).")
            else:
                log.error(f'Unknown action (by {self.user.nickname}): {action}')

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message
        }))

    @database_sync_to_async
    def get_conversation(self, conversation_id):
        return chat.Conversation.objects.get(id=conversation_id)

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
        'conversation': message.conversation_id,
        'author': {
            'id': message.author.id,
            'nickname': message.author.nickname,
            'pic': message.author.picture_thumbnail.url if message.author.picture else None,
            'url': message.author.get_absolute_url() if not message.author.is_anonymous else None,
        },
        'timestamp': message.creation.isoformat(),
    }
