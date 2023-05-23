from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone

from mockingJae_back import settings

from mockingJae_back.storages import S3Storage

class UserManager(BaseUserManager):
    def create_user_with_password(self, username, password):
        user = self.model(
            username = username,
            created_at = timezone.now(),
            is_staff = 0,
            is_superuser = 0,
            is_active = 0
        )

        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_user_with_instagram_id(self, username, instagram_id, instagram_username):
        user = self.model(
            username = username,
            created_at = timezone.now(),
            is_staff = 0,
            is_superuser = 0,
            is_active = 0,
            instagram_id = instagram_id,
            instagram_username = instagram_username
        )

        user.save(using = self._db)
        return user

    def create_user_with_apple_id(self, username, apple_id, apple_username):
        user = self.model(
            username = username,
            created_at = timezone.now(),
            is_staff = 0,
            is_superuser = 0,
            is_active = 0,
            apple_id = apple_id,
            apple_username = apple_username
        )

        user.save(using = self._db)
        return user
    
    def does_instagram_id_exist(self, instagram_id):
        return self.filter(instagram_id__exact = instagram_id).exists()

    def does_apple_id_exist(self, apple_id):
        return self.filter(apple_id__exact = apple_id).exists()
    
    def create_superuser(self, username, password):
        user = self.create_user_with_password(
            username = username,
            password = password
        )

        user.is_superuser = 1
        user.is_staff = 1
        user.is_active = 1
        user.save(using = self._db)
        return user
    
    def get_user_from_id(self, user_id):
        if (user := self.filter(id__exact = user_id)).exists():
            return user.get()
        return False
        
    def follow_user_from_id(self, user_id, target_user_id):
        if (user := self.get_user_from_id(user_id)) and (target_user := self.get_user_from_id(target_user_id)):
            user.followers.add(target_user)
            return True
        return False

    def unfollow_user_from_id(self, user_id, target_user_id):
        if (user := self.get_user_from_id(user_id)) and (target_user := self.get_user_from_id(target_user_id)):
            user.followers.remove(target_user)
            return True
        return False
    
    def undirected_follow(self, user_id, target_user_id):
        if (user := self.get_user_from_id(user_id)) and (target_user := self.get_user_from_id(target_user_id)):
            user.followers.add(target_user)
            target_user.followers.add(user)
            return True
        return False
    
    def undirected_unfollow(self, user_id, target_user_id):
        if (user := self.get_user_from_id(user_id)) and (target_user := self.get_user_from_id(target_user_id)):
            user.followers.remove(target_user)
            target_user.followers.remove(user)
            return True
        return False
    
    def get_followers(self, user_id):
        # return followers except for user_id
        if (user := self.get_user_from_id(user_id)):
            return user.followers.all()
        return False
    
    def get_followings(self, user_id):
        # return followings except for user_id
        if (user := self.get_user_from_id(user_id)):
            return user.followings.all()
        return False
    
    def get_followers_count(self, user_id):
        if (user := self.get_user_from_id(user_id)):
            return user.followers.count()
        return False
    
    def get_followings_count(self, user_id):
        if (user := self.get_user_from_id(user_id)):
            return user.followings.count()
        return False
    
    
    
    
class User(AbstractBaseUser):
    password = models.CharField(max_length = 128, null = True)
    username = models.CharField(max_length = 120, unique = True)
    last_login = models.DateTimeField(blank = True, null = True)
    created_at = models.DateTimeField()
    is_superuser = models.IntegerField(blank = True, null = True)
    is_active = models.IntegerField(blank = True, null = True)
    is_staff = models.IntegerField(blank = True, null = True)

    instagram_id = models.CharField(max_length = 120, blank = True, null = True, unique = True)
    instagram_username = models.CharField(max_length = 120, blank = True, null = True)
    apple_id = models.CharField(max_length = 120, blank = True, null = True, unique=True)
    apple_username = models.CharField(max_length = 120, blank = True, null = True)

    profile_image = models.ImageField(storage = settings.s3_storage, upload_to = 'profile_image', blank = True, null = True, default='profile_image/default.png')

    followers = models.ManyToManyField('self', symmetrical = False, related_name = 'followings')
    
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']

    def has_perm(self, perm, obj = None):
        return True
    
    def has_module_perms(self, app_label):
        return True

    class Meta:
        db_table = 'auth_user'
