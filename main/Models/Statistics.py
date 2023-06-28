from io import BytesIO
import json
import os
import shutil
from typing import Any, MutableMapping, Optional, Tuple

from django.db import models
from django.utils import timezone
from django.conf import settings
from main.BusinessLogics.Scrolls.timelines import IndexTimeline

from main.utils import create_tar_archive_with_parent_basename
from .UserModel import User
from .TaskModel import Task
from .ScrollsModel import Scrolls
from .RemixModel import Remix

from main import tasks
from mockingJae_back.settings import s3_storage



from django.core.files.storage import FileSystemStorage


class SessionManager(models.Manager):
    def update_end_time(self, session_id):
        session = self.get(id=session_id)

        if not session:
            return None
        
        session.end_time = timezone.now()
        session.save()
        return session
    
    def update_total_time(self, session_id):
        session = self.get(id=session_id)

        if not session:
            return None
        
        time_delta = session.end_time - session.start_time
        session.total_time = time_delta.total_seconds()

        session.save()
        return session
    
    def create_session(self, user_id):
        """
        Should be called every time user logs in
        """
        user = User.objects.get(id=user_id)

        if user is None:
            return None
        
        session = self.create(user=user, start_time=timezone.now(), end_time=timezone.now())
        session.save()
        self.update_total_time(session.id)
        session.save()
        return session
    
    def get_session_from_user(self, user_id):
        user = User.objects.get(id=user_id)

        if user is None:
            return None
        
        recent_user_session = self.filter(user=user).order_by('-start_time').first()


        if recent_user_session is None:
            return None
        
        return recent_user_session
    
    def session_update_from_remix(self, user_id, remix_id):
        """
        Update session with remix information
        This will be called after every remix creation 
        """
        session = self.get_session_from_user(user_id)
        scrolls_view_details = ViewedScrollsStatistic.objects.create_scrolls_view_detail(remix_id)
        
        if session is None:
            return None
                
        if scrolls_view_details is None:
            return None

        session.viewed_scrolls_statistics.add(scrolls_view_details)
        
        # Time information update in the session
        session = self.update_end_time(session.id)
        session.save()

        session = self.update_total_time(session.id)
        session.save()

        return session

class ViewedScrollsStatisticManager(models.Manager):
    def create_scrolls_view_detail(self, remix_id):
        remix = Remix.objects.get(id=remix_id)

        if remix is None:
            return None
        
        scrolls = remix.scrolls
        scrolls_view_details = self.create(scrolls=scrolls, timeline=remix.task_queue_json, viewed_at = timezone.now(), time_spent = 0.0)
        scrolls_view_details.save()


        timeline = scrolls_view_details.timeline
        timeline_json = json.loads(timeline)['timeline']['first']

        scrolls_view_details.time_spent = 0
        
        scrolls_view_details.save()

        return scrolls_view_details


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


class ViewedScrollsStatistic(models.Model):
    time_spent = models.FloatField(default=0)
    scrolls = models.ForeignKey(Scrolls, on_delete=models.CASCADE)
    timeline = models.TextField(null=True, blank=True)

    viewed_at = models.DateTimeField(auto_now_add=True)

    objects = ViewedScrollsStatisticManager()

    def get_timeline(self):
        timeline_json = json.loads(self.timeline)['timeline']['first']
        return timeline_json

    def get_length(self):
        length = json.loads(self.timeline)['length']
        return length

    def get_relative_length(self):
        """
        remix length / total length
        """
        pass

class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_scrolls_statistics = models.ManyToManyField(ViewedScrollsStatistic, related_name='sessions')

    total_time = models.FloatField(default=0, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True) # will be updated after each scrolls view

    objects = SessionManager()



