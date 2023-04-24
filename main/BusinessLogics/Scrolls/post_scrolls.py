from django.utils import timezone

from rest_framework.response import Response
from rest_framework import status, exceptions


from main.models import Scrolls, User
from main.serializer import *
from main import tasks

class RestApiCallback:
    def __init__(self, status):
        # status should be a valid Django Rest Api status object
        self.status = status
    
    def callback(self, message):
        # message should be a valid json form
        # ex) message = {'task_id': f'{conversion_task_id}'}
        return Response(message, 
                    status=self.status)

def upload_video(data, success_callback, fail_callback):
    """
    Uploads the video requested and starts conversion.
    If successfully launched, the method returns the
    convertion task id. This does not garauntees the
    success of the video conversion.
    """
    try:
        assert(data['video_to_upload'] and data['title'])

        unprocessed_video = data['video_to_upload']
        title = data['title']
        # only in production!
        user_id = 1
            # in production,
        # user_id = user_id from token

        video = VideoMedia.objects.create(video=unprocessed_video, title=title, user_id=user_id)

        if not video:
            return fail_callback.callback({'message': 'error occured during video uploading'})

        if conversion_task_id := VideoMedia.objects.convert(video.id):
            return success_callback.callback({'task_id': f'{conversion_task_id}'})
            
        VideoMedia.objects.delete(video.id)

    except:
        return fail_callback.callback({'message': 'argument missing'})

    
def scrollify_video(data, success_callback, fail_callback, wait = False):
    """
    If called in the right order, this method should have been called
    after the upload_video method.
    """

    try:
        task_id = data['task_id']
        title = data['title']
        height = data['height']
        fps = data['fps']
        quality = int(data['quality'])
        media_id = tasks.get_result_from_task_id(task_id)

        if tasks.task_status(task_id) in [3,4]:
            return fail_callback.callback({'message': 'task is being run or waiting inside the queue'})

        if not media_id:
            VideoMedia.objects.delete(media_id)
            return fail_callback.callback({'message': 'error occured in conversion process, try uploading again'})
        
        scrolls_object = Scrolls.objects.create(media_id=media_id, title=title, height=height)
        
        if not scrolls_object:
            return fail_callback.callback({'message': 'media object does not exist, possibly deleted'})
        
        if wait and (scrollify_directory := VideoMedia.objects.mp4_to_scrolls(media_id=media_id, scrolls_id=scrolls_object.id, fps=fps, quality=quality, wait=True)):
            return success_callback.callback({'message': 'scrollify task successfully launched', 'scrolls_directory': scrollify_directory, 'scrolls_id': scrolls_object.id})
        elif scrollify_task_id := VideoMedia.objects.mp4_to_scrolls(media_id=media_id, scrolls_id=scrolls_object.id, fps=fps, quality=quality):
            return success_callback.callback({'message': 'scrollify task successfully launched', 'task_id': scrollify_task_id, 'scrolls_id': scrolls_object.id})
        

        # This deletes not only the scrolls but also related VideoMedia too.
        # Users have to re-upload from the begining when they reach here.
        Scrolls.objects.delete(scrolls_object.id)
        
        return fail_callback.callback({'message': 'scrollify process not launched, try uploading again'})
    
    except:
        return fail_callback({'message': 'argument missing'})



def upload_scrolls(data, success_callback, fail_callback):
    """
    """
    scrolls_dirname = data.get('scrolls_directory')

    if not scrolls_dirname:
        return _upload_with_task_id(data, success_callback, fail_callback)
        
    try:
        scrolls_id = data['scrolls_id']

        if (upload_task_id := Scrolls.objects.upload(scrolls_id=scrolls_id, scrolls_dirname=scrolls_dirname, wait=False, ipfs=False)):
            return success_callback.callback({'message': 'scrollify task successfully launched', 'task_id': upload_task_id})
        
        return fail_callback.callback({'message': f'scrolls with id {scrolls_id} not found, try uploading again'})
    except:
        return fail_callback.callback({'message': 'argument missing'})

def _upload_with_task_id(data, success_callback, fail_callback):
    try:
        task_id = data['task_id']
        scrolls_id = data['scrolls_id']

        if tasks.task_status(task_id) in [3,4]:
            return fail_callback.callback({'message': 'task is being run or waiting inside the queue'})
        
        scrolls_dirname = tasks.get_result_from_task_id(task_id)
        
        if not scrolls_dirname:
            return fail_callback.callback({'message': 'scrollify process was not successful, try uploading again'})
        
        if (upload_task_id := Scrolls.objects.upload(scrolls_id=scrolls_id, scrolls_dirname=scrolls_dirname, wait=False, ipfs=False)):
            return success_callback.callback({'message': 'scrollify task successfully launched', 'task_id': upload_task_id})
        
        return fail_callback.callback({'message': f'scrolls with id {scrolls_id} not found, try uploading again'})
    except:
        return fail_callback.callback({'message': 'argument missing'})