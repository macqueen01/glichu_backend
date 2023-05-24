from io import BytesIO
import os
import shutil

from django.db import models
from django.utils import timezone
from django.conf import settings

from main.utils import create_tar_archive_with_parent_basename
from ..UserModel import User
from ..TaskModel import Task

from main import tasks
from mockingJae_back.settings import s3_storage



from django.core.files.storage import FileSystemStorage

class Voice(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    content = models.TextField(max_length=20)
    addressing_scrolls = models.ForeignKey('Scrolls', on_delete=models.CASCADE, null=True)
    
