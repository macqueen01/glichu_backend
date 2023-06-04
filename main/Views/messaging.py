from django.utils import timezone

from rest_framework.response import Response
from rest_framework import status, exceptions
from notifications.signals import notify

from main.Models.Message import MessageManager


from main.models import Scrolls, User, Message
from main.serializer import *
from main import tasks

from main.Views.authentications import authenticate_then_user_or_unauthorized_error



def send_message(request):
    user = authenticate_then_user_or_unauthorized_error(request)
    
    if request.method != 'POST':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    try:
        target_id = request.data['target_id']
        message = request.data['message']
        remix_id = request.data['remix']

        remix = Remix.objects.get(id = remix_id)

        if not remix:
            return Response({'message': 'remix is invalid'}, status=status.HTTP_400_BAD_REQUEST)

        remix_messages = Message.objects.get_message_of_remix(remix_id)

        if remix_messages and remix_messages.filter(sender__id = user.id).filter(receiver__id = target_id).exists():
            return Response({'message': 'already sent'}, status=status.HTTP_400_BAD_REQUEST)

        Message.objects.create(sender = user, receiver = User.objects.get_user_from_id(target_id), message = message, remix = Remix.objects.get(id = remix_id))
        
        
        try:
            notify.send(user, recipient=User.objects.get_user_from_id(target_id), verb='sent you a message', action_object=remix)
        except Exception as e:
            print(e)

        return Response({'message': 'message sent'}, status=status.HTTP_200_OK)
    except:
        return Response({'message': 'argument missing'}, status=status.HTTP_400_BAD_REQUEST)

