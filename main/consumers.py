import asyncio
import json 

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User


from notifications.signals import notify


from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync

from django.contrib.auth.models import User
from notifications.models import Notification

from main.Views.authentications import authenticate_then_user_or_none_for_websocket
from main.serializer import NotificationSerializerGeneralUse


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Accept the WebSocket connection
        await self.accept({
            'type': 'websocket.accept'
        }) 


        user = await authenticate_then_user_or_none_for_websocket(self.scope)
        
        print(user)

        if not user:
            self.close()
            return

        
        # Subscribe the user to their own channel
        await self.channel_layer.group_add(
            f'user_{user.id}',
            self.channel_name
        )

        # Fetch and send all stored notifications to the user
        await self.fetch_notifications(user.id)


    
    async def disconnect(self, close_code):
        # Unsubscribe the user from their own channel

        print(close_code)

        user = await authenticate_then_user_or_none_for_websocket(self.scope)
        
        if not user:
            await self.close()
            return
        
        if hasattr(self, 'heartbeat_task'):
            self.heartbeat_task.cancel()
            await asyncio.wait([self.heartbeat_task])
        
        await self.channel_layer.group_discard(
            f'user_{user.id}',
            f"user-{user.id}-notifications"
        )
    

    def receive(self, text_data):
        # No action needed when receiving messages from the client
        pass


    def send_heartbeat(self):
        while True:
            try:
                self.send('heartbeat')
                asyncio.sleep(10)  # Send heartbeat every 10 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Handle any errors that occur while sending the heartbeat
                print(f"Error sending heartbeat: {str(e)}")
                break


    @database_sync_to_async
    def get_notifications(self, user_id):
        # Retrieve notifications for the user from the database
        serializer = NotificationSerializerGeneralUse
        lst = []

        for notification in Notification.objects.filter(recipient_id=1):
            notification = serializer(notification).data
            lst.append(notification)
        
        return lst


    async def send_notification(self, notifications):
        # Send the notification message to the client

        jsonified_notification = await sync_to_async(json.dumps)(notifications)
        print(jsonified_notification)
        
        await self.send(text_data=jsonified_notification)



    async def fetch_notifications(self, user_id):
        # Fetch and send all stored notifications to the client
        notifications = await self.get_notifications(user_id)
        print(notifications)
        await self.send_notification(notifications)


    def notification_handler(self, event):
        # Handle the 'notify' signal event and send the notification to the client
        self.send_notification(event['notification'])



