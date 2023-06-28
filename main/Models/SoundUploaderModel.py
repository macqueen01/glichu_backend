from django.db import models
from .UserModel import User

class ExternalUploader(models.Model):
    source = models.CharField(max_length=255) # freesound
    username = models.CharField(max_length=255)
    profile_image = models.CharField(max_length=255, null=True, blank=True) # url to profile image if exists
    profile_url = models.CharField(max_length=255, null=True, blank=True) # external url to profile if exists

class SoundUploader(models.Model):
    is_internal = models.IntegerField(default=1) # 1 if internal user, and 0 if not 
    internal_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'identifier')
    external_user = models.ForeignKey(ExternalUploader, on_delete=models.CASCADE, related_name='identifier')



