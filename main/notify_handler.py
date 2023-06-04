from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



def notify_handler(sender, recipient, verb, action_object, **kwargs):
    # Save the notification to the database
    actor_content_type = ContentType.objects.get_for_model(sender)
    notification = Notification.objects.create(
        recipient=recipient,
        verb=verb,
        action_object=action_object,
        actor_content_type_id = actor_content_type.id,
    )

    # Retrieve the WebSocket channel name associated with the recipient
    channel_name = f'user_{recipient.id}'

    # Send the notification to the WebSocket consumer through the channel layer
    channel_layer = get_channel_layer()

    async def send_notification():
        notification_data = {
            'notification': {
                'id': notification.id,
                'message': f"You have a new {verb} from {sender}.",
                'action_object': action_object.id,
            }
        }
        await channel_layer.send(channel_name, {
            'type': 'notification.handler',
            'notification': notification_data,
        })

    async_to_sync(send_notification)()
