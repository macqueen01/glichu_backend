from io import BytesIO
import os

from django.db import models
from django.utils import timezone
from django.conf import settings

from main.utils import create_tar_archive_with_parent_basename
from .UserModel import User
from .TaskModel import Task

from main import tasks
from mockingJae_back.settings import s3_storage



from django.core.files.storage import FileSystemStorage

class RemixManager(models.Manager):

    def create_remix(self, title, user, scrolls, remix_directory):
        remix = self.create(title=title, user=user, scrolls=scrolls, remix_directory=remix_directory)
        return remix
    
    def get_all_remixes_of_user(self, user):
        return self.filter(user=user).all()
    
    def get_all_remixes_of_scrolls(self, scrolls_id):
        return self.filter(scrolls=scrolls_id).all()
    
    def remix_to_video(output_path, remix):
        if auto_recording_task := tasks.remix_to_video.delay(
            output_path = output_path,
            remix = remix
        ):
            return auto_recording_task.id
        return False
    

class RemixManager_DEBUG(models.Manager):

    def create_remix(self, title, scrolls, remix_directory):
        user = User.objects.get(id=1)
        remix = self.create(title=title, user=user, scrolls=scrolls, remix_directory=remix_directory)
        remix.save()
        return remix
    
    def remix_to_video(output_path, remix):
        if auto_recording_task := tasks.remix_to_video.delay(
            output_path = output_path,
            remix = remix
        ):
            return auto_recording_task.id
        return False

class Remix(models.Model):
    """
    Remix model for storing the remixes.
    """

    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    remix_directory = models.CharField(max_length=500, null=True, default='/')
    created_at = models.DateTimeField(auto_now_add=True)
    scrolls = models.ForeignKey('Scrolls', on_delete=models.CASCADE, null=True)

    objects = RemixManager_DEBUG()

    def __str__(self):
        return self.title

    


