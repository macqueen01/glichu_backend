from django.db import models

from .ScrollsModel import Scrolls, Tag

class SoundManager(models.Manager):
    pass



class Sound(models.Model):
    title = models.CharField(max_length = 500)
    source = models.CharField(max_length=255)
    sound_type = models.CharField(max_length=255, default = 'event') # 'background' or 'event'
    is_downloaded = models.IntegerField(default = 0)
    thumbnail = models.CharField(max_length = 500, null = True, blank=True)
    used_in = models.ManyToManyField(Scrolls, related_name = 'featured_sounds')

    tag = models.ManyToManyField(Tag, related_name = 'tagged_sounds')
    
    duration = models.FloatField()
    loopable = models.IntegerField(default = 0)
    url = models.CharField(max_length=500, null=True, blank=True)


