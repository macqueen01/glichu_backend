from django.utils import timezone

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


            date = timezone.now().date().__str__().replace('-', '')

            timeline_json = request.data['timeline']
            title = request.data['title']
            length = int.parse(request.data['length'])
            scrolls = int.parse(request.data['scrolls'])

            timeline = IndexTimeline(
                timeline_json=timeline_json,
                title=title,
                length=length,
            )

            remix = RemixInMemory(
                title = title,
                timeline=timeline,
                scrolls_id=scrolls
            )

            remix_path = os.path.join(
                settings.MEDIA_ROOT, 
                f'auto_recordings/{date}/{remix.get_title}'
            )

            if auto_recording_task := tasks.remix_to_video.delay(
                output_dir = remix_path,
                remix = remix
            ):
                return Response({
                    'message': 'task launched successful',
                    'task_id': f'{auto_recording_task.id}'
                    },status = status.HTTP_200_OK)
                
            return Response({'message': 'task launch unsuccessful'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except:
        return Response({'message': 'argument missing'}, 
            status=status.HTTP_400_BAD_REQUEST)


