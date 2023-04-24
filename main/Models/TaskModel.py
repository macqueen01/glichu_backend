from io import BytesIO
import os

from django.db import models
from django.utils import timezone
from django.conf import settings

from main.utils import create_tar_archive_with_parent_basename
from .UserModel import User

from main import tasks
from mockingJae_back.settings import s3_storage



from django.core.files.storage import FileSystemStorage

# Model Keywords

class TaskKeywords:
    VIDEO_CONVERT_TASK = 'video_convert'
    SCROLLS_UPLOAD_TASK = 'scrolls_upload'
    SCROLLS_CONVERT_TASK = 'scrolls_convert'

# Model Managers

class TaskManager(models.Manager):

    def create_task(self, created_by, task_type, task_id):
        task = self.create(created_by=created_by, task_type=task_type, task_id=task_id)
        task.save()
        return task

    def get_task(self, task_id):
        try:
            return self.get(task_id=task_id)
        except:
            return None

    def update_task(self, task_id, status):
        task = self.get_task(task_id)
        if task:
            task.status = status
            task.save()
            return task
        else:
            return None

    def delete_task(self, task_id):
        task = self.get_task(task_id)
        if task:
            task.delete()
            return True
        else:
            return False
    
    def get_recent_tasks(self, user_id, num_tasks=10):
        # returns the num_task most recent tasks of the user
        # if the number of task < num_tasks, returns all tasks
        tasks = self.filter(created_by=user_id).order_by('-created_at')[:num_tasks]
        return tasks

    def get_recent_scrolls_upload_tasks(self, user_id, num_tasks=10):
        # returns the num_task most recent tasks of the user
        # if the number of task < num_tasks, returns all tasks
        tasks = self.filter(created_by=user_id, task_type='scrolls_upload').order_by('-created_at')[:num_tasks]
        return tasks
    
    def get_recent_video_convert_tasks(self, user_id, num_tasks=10):
        # returns the num_task most recent tasks of the user
        # if the number of task < num_tasks, returns all tasks
        tasks = self.filter(created_by=user_id, task_type='video_convert').order_by('-created_at')[:num_tasks]
        return tasks
    
    def get_recent_scrolls_convert_tasks(self, user_id, num_tasks=10):
        # returns the num_task most recent tasks of the user
        # if the number of task < num_tasks, returns all tasks
        tasks = self.filter(created_by=user_id, task_type='scrolls_convert').order_by('-created_at')[:num_tasks]
        return tasks

    def task_resume_suggestion(recent_task):
        """
        Returns the suggested task to resume
        
        If the recent task is video_convert,
        this method suggests scrolls_convert.
        """
        if recent_task.task_type == 'video_convert':
            return 'scrolls_convert'
        elif recent_task.task_type == 'scrolls_convert':
            return 'scrolls_upload'
        return 'video_convert'
    

    
    

class Task(models.Model):
    # task_type:
    #   1. 'video_convert'
    #   2. 'scrolls_convert'
    #   3. 'scrolls_upload'

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    task_id = models.CharField(max_length=100, unique=True, primary_key=True)
    task_type = models.CharField(max_length=100, default='')

    objects = TaskManager()

        
