from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, username, name, password):
        user = self.model(
            name = name,
            username = username,
            created_at = timezone.now(),
            is_staff = 0,
            is_superuser = 0,
            is_active = 0
        )

        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self, username, name, password):
        user = self.create_user(
            name = name,
            username = username,
            password = password
        )

        user.is_superuser = 1
        user.is_staff = 1
        user.is_active = 1
        user.save(using = self._db)
        return user
        
    
class User(AbstractBaseUser):
    password = models.CharField(max_length = 128)
    username = models.CharField(max_length = 120, unique = True)
    name = models.CharField(max_length = 20)
    last_login = models.DateTimeField(blank = True, null = True)
    created_at = models.DateTimeField()
    is_superuser = models.IntegerField(blank = True, null = True)
    is_active = models.IntegerField(blank = True, null = True)
    is_staff = models.IntegerField(blank = True, null = True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']

    def has_perm(self, perm, obj = None):
        return True
    
    def has_module_perms(self, app_label):
        return True

    class Meta:
        db_table = 'auth_user'
