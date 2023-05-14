from django.utils import timezone
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status, exceptions
from main.BusinessLogics.Scrolls.timelines import IndexTimeline
from main.BusinessLogics.Scrolls.timelines import Remix as RemixInMemory


from main.models import Scrolls, User
from main.serializer import *
from main import tasks



def upload_auto_recording(request):
    try:
        if request.method == 'POST':
            
            assert(request.data['timeline'] and 
                   request.data['title'] and 
                   request.data['length'] and
                   request.data['scrolls'])

            if task := tasks.remix_to_video.delay(json=request.data):
                return Response({
                    'message': 'task launched successful',
                    'task_id': f'{task.id}'
                    }, status = status.HTTP_200_OK)
                
            return Response({'message': 'task launch unsuccessful'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except:
        return Response({'message': 'argument missing'}, 
            status=status.HTTP_400_BAD_REQUEST)


