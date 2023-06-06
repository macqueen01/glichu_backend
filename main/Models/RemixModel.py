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
        
        # Default permission is not private to only remix creator
        permission = RemixPermission.objects.create(remix=remix)
        permission.save()
        
        return remix
    
    def get_all_remixes_of_user(self, user):
        return self.filter(user=user).all()
    
    def get_all_remixes_of_scrolls(self, scrolls_id):
        return self.filter(scrolls=scrolls_id)
    
    def get_thumbnail_url(self, remix_id):
        
        if not self.is_uploaded(remix_id):
            return None
        
        remix = self.get(id=remix_id)
        scrolls = remix.scrolls
        scrolls_dir = scrolls.scrolls_dir

        if scrolls_dir[-1] == '/':
            scrolls_dir = scrolls_dir[:-1]

        thumbnail_dir = f'{scrolls_dir}/1.jpeg'

        return thumbnail_dir

    def is_uploaded(self, remix_id):
        remix = self.get(id=remix_id)

        if remix and remix.uploaded_to_s3:
            return True

        return False
    
    def upload_remix(self, remix_id):
        remix = self.get(id=remix_id)

        try:
            if remix == None:
                return False
            
            if self.is_uploaded(remix_id):
                return False
            
            remix_directory = remix.remix_directory
            scrolls_id = remix.scrolls.id
            title = remix.title

            new_directory = f'auto-recording/{scrolls_id}/{title}'

            with open(remix_directory, 'rb') as f:
                s3_storage.save(new_directory, f)
                remix.uploaded_to_s3 = 1
                remix.remix_directory = new_directory
                remix.save()
                os.remove(remix_directory)
                return True
        
        
        except:
            return False
        

    def raise_remix_report(self, user_id, remix_id):
        if (user := User.objects.get_user_from_id(user_id)) and (remix := Remix.objects.get(id = remix_id)):
            user.reported_remixes.add(remix)
            user.save()
            return True
        return False
        
    def resolve_remix_report(self, user_id, remix_id):
        if (user := User.objects.get_user_from_id(user_id)) and (remix := self.get(id = remix_id)):
            user.reported_remixes.remove(remix)
            user.save()
            return True
        return False
    

    def like_remix(self, user_id, remix_id):

        user = User.objects.get_user_from_id(user_id)
        remix = Remix.objects.get(id=remix_id)

        if (user == None):
            return None
        
        if (remix == None):
            return None
        
        if (user in remix.liked_by.all()):
            return None
        
        remix.liked_by.add(user)
        remix.save()

        return remix
    
    def unlike_remix(self, user_id, remix_id):

        user = User.objects.get_user_from_id(user_id)
        remix = Remix.objects.get(id=remix_id)

        if (user == None):
            return None
        
        if (remix == None):
            return None
        
        if (user not in remix.liked_by.all()):
            return None
        
        remix.liked_by.remove(user)
        remix.save()

        return remix
    
    def does_user_like_remix(self, user_id, remix_id):

        user = User.objects.get_user_from_id(user_id)
        remix = Remix.objects.get(id=remix_id)

        if (user == None):
            return None
        
        if (remix == None):
            return None
        
        if (user in remix.liked_by.all()):
            return True
        
        return False
        

class RemixPermissionManager(models.Manager):

    def give_remix_permission_to_scrolls_uploader(self, remix_id):
        remix = Remix.objects.get(id=remix_id)

        if (remix == None):
            return None
        
        remix_permission = self.get(remix__id = remix_id)

        if (remix_permission == None):
            remix_permission = self.create(remix=remix, user_id=remix.scrolls.user.id, remix_uploader_has_access=1)
        
        remix_permission.scrolls_uploader_has_access = 1
        remix_permission.save()
        return remix_permission
    
    def give_remix_permission_to_all_users(self, remix_id):
        remix = Remix.objects.get(id=remix_id)

        if (remix == None):
            return None
        
        remix_permission = self.get(remix__id = remix_id)

        if (remix_permission == None):
            remix_permission = self.create(remix=remix, all_users_have_access=1)

        remix_permission.all_users_have_access = 1
        remix_permission.save()
        return remix_permission
    


    

class RemixManager_DEBUG(RemixManager):

    def create_remix(self, title, scrolls, remix_directory):
        user = User.objects.get(id=1)
        remix = self.create(title=title, user=user, scrolls=scrolls, remix_directory=remix_directory)
        remix.save()
        return remix
    


class Remix(models.Model):
    """
    Remix model for storing the remixes.
    """

    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    remix_directory = models.CharField(max_length=500, null=True, default='/')
    uploaded_to_s3 = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    scrolls = models.ForeignKey('Scrolls', on_delete=models.CASCADE, null=True)

    task_queue_json = models.TextField(null=True, default='{}')
    length = models.IntegerField(null=True, default=0)

    liked_by = models.ManyToManyField(User, related_name='liked_remixes', null = True)
    saved_by_scrolls_uploader = models.IntegerField(default=0)

    reported_by = models.ManyToManyField(User, related_name='reported_remixes', null = True)

    objects = RemixManager()

    def __str__(self):
        return self.title
    

class RemixPermission(models.Model):
    """
    Remix permission model stores
        - if scrolls uploader has access to the remix
        - if remix uploader has let other viewers to have access to the remix 
    """

    remix = models.ForeignKey(Remix, on_delete=models.CASCADE)
    scrolls_uploader_has_access = models.IntegerField(default=0)
    all_users_have_access = models.IntegerField(default=0)

    objects = RemixPermissionManager()

    def __str__(self):
        return self.remix.title

    


