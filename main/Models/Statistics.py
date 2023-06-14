from io import BytesIO
import os
import shutil
from typing import Any, MutableMapping, Optional, Tuple

from django.db import models
from django.utils import timezone
from django.conf import settings

from main.utils import create_tar_archive_with_parent_basename
from .UserModel import User
from .TaskModel import Task

from main import tasks
from mockingJae_back.settings import s3_storage



from django.core.files.storage import FileSystemStorage


class DailyVisitManager(models.Manager):
    def create_daily_visit(self, user):
        daily_visit = self.create(user=user, date=timezone.now())
        daily_visit.save()
        return daily_visit

    def get_daily_visit_by_date(self, date):
        striped_date = date.strftime("%Y-%m-%d")
        return self.filter(date=striped_date).all()
    
    def get_daily_visit_by_user(self, user):
        return self.filter(user=user).all()
    
    def get_daily_visit_by_user_and_date(self, user, date):
        striped_date = date.strftime("%Y-%m-%d")
        return self.filter(user=user, date=striped_date).all()
    
    def get_num_visit_by_user_and_date(self, user, date):
        return self.filter(user=user, date=date).count()
    
    def get_num_visit_in_range(self, user, start_date, end_date):
        return self.filter(user=user, date__range=[start_date, end_date]).count()
    
    def get_num_visit_by_date_unique_user(self, date):
        return self.filter(date=date).distinct('user').count()
    
    def active_user_in_range(self, start_date, end_date):
        return self.filter(date__range=[start_date, end_date]).distinct('user').count()
    
    def monthly_active_user(self, date):
        return self.filter(date__month=date.month).distinct('user').count()
    
    def weekly_active_user(self, date):
        return self.filter(date__week=date.week).distinct('user').count()
    
    def daily_active_user(self, date):
        return self.filter(date=date).distinct('user').count()
    

class DailyVisit(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = DailyVisitManager()

    def __str__(self):
        return self.date.strftime("%Y-%m-%d")

    class Meta:
        ordering = ['-date']