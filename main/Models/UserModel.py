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

    def create_user_with_apple_id(self, username, apple_id):
        user = self.model(
            username = username,
            created_at = timezone.now(),
            is_staff = 0,
            is_superuser = 0,
            is_active = 0,
            apple_id = apple_id,
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
    
    def raise_user_report(self, user_id, user_reported):
        if (user := self.get_user_from_id(user_id)) and (user_reported := self.get_user_from_id(user_reported)):

            if (user_reported in user.reported.all()):
                return False
            
            user_reported.reported_by.add(user)
            user_reported.save()
            return True
        return False
    
    def reset_username(self, user_id, username):
        user = self.get_user_from_id(user_id)
        user.username = username
        user.save()
        return user
    
    def accept_invitation(self, candidate_id, inviter_id):
        inviter = self.get_user_from_id(inviter_id)
        candidate = self.get_user_from_id(candidate_id)
        
        if (not inviter or not candidate):
            return False
        
        if (candidate in inviter.invited.all()):
            return False
        
        if (candidate.is_invited == 0):
            candidate.invited_at = timezone.now()
        
        inviter.invited.add(candidate)
        candidate.is_invited = 1
        candidate.save()
        inviter.save()

        self.follow_user_from_id(inviter_id, candidate_id)
        self.follow_user_from_id(candidate_id, inviter_id)

        return True
    
        
    def get_user_from_id(self, user_id):
        if (user := self.filter(id__exact = user_id)).exists():
            return user.get()
        return False
        
    def follow_user_from_id(self, user_id, target_user_id):
        if (user := self.get_user_from_id(user_id)) and (target_user := self.get_user_from_id(target_user_id)):
            target_user.followers.add(user)
            return True
        return False

    def unfollow_user_from_id(self, user_id, target_user_id):
        if (user := self.get_user_from_id(user_id)) and (target_user := self.get_user_from_id(target_user_id)):
            target_user.followers.remove(user)
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
            return user.followers.exclude(id = user_id).all()
        return False
    
    def get_followings(self, user_id):
        # return followings except for user_id
        if (user := self.get_user_from_id(user_id)):
            return user.followings.exclude(id = user_id).all()
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
    tagger = models.ForeignKey('self', on_delete=models.SET_DEFAULT, default=None, null = True)

    invited = models.ManyToManyField('self', symmetrical = False, related_name = 'invited_by')
    is_invited = models.IntegerField(blank = True, null = True, default=0)
    invited_at = models.DateTimeField(blank = True, null = True)


    reported_by = models.ManyToManyField('self', symmetrical = False, related_name = 'reported')
    
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']

    def has_perm(self, perm, obj = None):
        return True
    
    def has_module_perms(self, app_label):
        return True

    class Meta:
        db_table = 'auth_user'
