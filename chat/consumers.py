import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Chat, User
from django.utils import timezone
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'chat_{self.user_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        print(f"Received message: {text_data}")  # Log the incoming message
        try:
            text_data_json = json.loads(text_data)
            action = text_data_json['action']
            if action == 'authenticate':
                print(f"User {self.user_id} online")
            if action == 'send-chat-message':
                message = text_data_json['data']['message']
                sender = text_data_json['data']['sender']  # Admin (1) or User (0)

                # Save the message to the database
                user = await sync_to_async(User.objects.get)(id=self.user_id)
                await sync_to_async(Chat.objects.create)(
                    user=user,
                    message=message,
                    time=timezone.now(),
                    sender=sender,
                    is_user_read=False if sender == 1 else True,  # Mark unread for the recipient
                    is_admin_read=False if sender == 0 else True
                )

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'sender': sender
                    }
                )
            if action == 'seen':
                sender = text_data_json['sender']
                if sender == 0:
                    await sync_to_async(Chat.objects.filter)(user_id=self.user_id, sender=1, is_user_read=False).update(is_user_read=True)
                elif sender == 1:
                    await sync_to_async(Chat.objects.filter)(user_id=self.user_id, sender=0, is_admin_read=False).update(is_admin_read=True)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        except Exception as e:
            print(f"Error: {e}")
            
    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'action': 'send-chat-message', 'data': {
            'message': message,
            'sender': sender
        }}))
