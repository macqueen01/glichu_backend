from django.db import models
from .UserModel import User

from main.BusinessLogics.freesound_fetch import *

class SoundUploaderManager(models.Manager):

    def create_freesound_uploader_min(self, freesound_uploader_username):
        freesound_uploader = ExternalUploader.objects.create(
            source='freesound', 
            username=freesound_uploader_username)
        freesound_uploader.save()

        new_uploader = self.create(is_internal=0, external_user=freesound_uploader)
        new_uploader.save()

        return new_uploader

    def create_freesound_uploader(self, freesound_uploader_username):
        freesound_uploader = freesound_get_user(freesound_uploader_username)

        if (freesound_uploader == None):
            return None
        
        freesound_uploader = ExternalUploader.objects.create(
            source='freesound', 
            username=freesound_uploader.username, 
            profile_image=freesound_uploader.avatar.small, 
            profile_url=freesound_uploader.url
            )
        freesound_uploader.save()

        new_uploader = self.create(is_internal=0, external_user=freesound_uploader)
        new_uploader.save()

        return new_uploader
    
    def get_uploader(self, username):
        internal_uploader = self.filter(internal_user__username=username)
        external_uploader = self.filter(external_user__username=username)

        if (not internal_uploader.exists() and not external_uploader.exists()):
            return (None, None)
        
        
        internal_uploader = internal_uploader.first() if internal_uploader.exists() else None
        external_uploader = external_uploader.first() if external_uploader.exists() else None
        
        return (internal_uploader, external_uploader)
        

class ExternalUploader(models.Model):
    source = models.CharField(max_length=255) # freesound
    username = models.CharField(max_length=255)
    profile_image = models.CharField(max_length=255, null=True, blank=True) # url to profile image if exists
    profile_url = models.CharField(max_length=255, null=True, blank=True) # external url to profile if exists

class SoundUploader(models.Model):
    is_internal = models.IntegerField(default=1) # 1 if internal user, and 0 if not 
    internal_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'identifier', null=True, blank=True)
    external_user = models.ForeignKey(ExternalUploader, on_delete=models.CASCADE, related_name='identifier', null=True, blank=True)

    objects = SoundUploaderManager()


