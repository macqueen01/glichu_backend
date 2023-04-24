from django.utils import timezone

from rest_framework.response import Response
from rest_framework import status, exceptions


from main.models import Scrolls, User, Task, TaskKeywords
from main.serializer import *
from main import tasks

def the_most_recent_task(request):
    """
    Returns the recent task launched by the user
    """
    try:
        if request.method == 'GET':
            user_id = 1
            # in production,
            # user_id = user_id from token
            task = Task.objects.get_recent_tasks(user_id=user_id, num_tasks=1)[0]
            if task:
                return Response({'task_id': f'{task.task_id}, task_type: {task.task_type}'}, 
                    status=status.HTTP_200_OK)
            else:
                return Response({'message': 'no recent task'}, 
                    status=status.HTTP_200_OK)
        return Response({'message': 'wrong method call'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED)

    except:
        return Response({'message': 'argument missing'}, 
            status=status.HTTP_400_BAD_REQUEST)

"""
def task_suggest(request):

    recent_task = Task.objects.get_recent_tasks(user_id=1, num_tasks=1)

    if not recent_task:
        return Response({'message': 'no recent task'}, 
            status=status.HTTP_200_OK)
    
    recent_task = recent_task[0]

    task_resume_suggestion = Task.objects.task_resume_suggestion(recent_task.task_id)

    if TaskKeywords.VIDEO_CONVERT_TASK == task_resume_suggestion:
        return Response({'message': 'no recent task'}, 
            status=status.HTTP_200_OK)
    
    if TaskKeywords.SCROLLS_CONVERT_TASK == task_resume_suggestion:
        return Response({'message': f'need to convert to scrolls. Task id: {recent_task.task_id}',}, 
            status=status.HTTP_200_OK)

    if TaskKeywords
"""