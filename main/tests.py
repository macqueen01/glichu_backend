from django.test import TestCase, Client
from django.test.client import encode_multipart
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase, APIClient

from celery.result import AsyncResult

from main.models import VideoMedia
from main.views import video_upload

import os, time



def path_checker(path):
    """
    Helper function to return True iff path exists
    """
    is_string = isinstance(path, str)
    try:
        print(f'{path} object is {type(path)}, not a string')
        assert(is_string)
    except:
        return os.path.exists(path)



class UploadVideoTestCase(APITestCase):
    def test_upload_file_and_convert(self):

        url = '/scrolls/upload/video'
        date = timezone.now().date().__str__().replace('-', '')

        ARCHIVE_PATH = os.path.join(settings.MEDIA_ROOT, f'archive/video/{date}/first.mov')


        # Open a local file to use as the video to be uploaded
        with open('./test_assets/first.mov', 'rb') as f:
            # Create a SimpleUploadedFile instance using the local file
            uploaded_video = SimpleUploadedFile('first.mov', f.read())

        # Create a dictionary of form data
        data = {'video_to_upload': uploaded_video, 'title': 'My Video'}

        # Encode the request as multipart
        request = self.client.post(url, data, content_type='multipart/form-data')

        # Check the response status code
        self.assertEqual(request.data, 200)

        # Check that the response contains a task_id
        self.assertTrue('task_id' in request.data)

        # Assert
        self.assertEqual(request.data, status.HTTP_200_OK)

        task_id = request.content

        # Wait for the task to complete
        task_result = AsyncResult(task_id)
        while not task_result.ready():
            time.sleep(1)  # Wait for 1 second before checking the task status again
        
        encoded_path = task_result.result

        # check if the video model instance has been created
        self.assertEqual(VideoMedia.objects.filter(title__exact = 'FIRST SCROLL').exists(), True)

        uploaded_video = VideoMedia.objects.filter(title__exact = 'FIRST SCROLL').get()

        # check if the video is encoded
        self.assertEqual(VideoMedia.objects.is_media_converted(uploaded_video.id), True)
    

        # revert all changes happened during the test
        VideoMedia.objects.complete_delete(uploaded_video.id)


