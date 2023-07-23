import json
import os 

from django.db import models
import requests

from main.Models.SoundUploaderModel import SoundUploader
from main.Models.UserModel import User
from mockingJae_back.settings import s3_client, s3_main_bucket
from .ScrollsModel import Scrolls, Tag

class SoundManager(models.Manager):
    def download_sound_to_s3(self, sound_id):
        sound = self.get(id=sound_id)
        
        sound_url = sound.url
        sound_id = sound.id

        # configure {sound_id}_upload.json
        request_json = {
            'url': sound_url,
            'id': sound_id,
        }

        result = requests.post(
            os.environ.get('AWS_API_GATEWAY_UPLOAD_SOUND_URL'),
            data = json.dumps(request_json)
        )

        if result.status_code != 200:
            return False
        
        sound.url = os.environ.get('AWS_S3_BASE_URL') + f'/audio/{sound_id}.mp4'
        sound.is_downloaded = 1
        return True

    def create_from_freesound(self, freesound_sound, is_background = False, loopable = False):
        sound_uploader_username = freesound_sound['username']
        tags = freesound_sound['tags']

        if (existing_sound := Sound.objects.filter(internal_id = freesound_sound['id'])).exists():
            return existing_sound.first()

        internal_uploader, external_uploader = SoundUploader.objects.get_uploader(sound_uploader_username)
        
        if not external_uploader:
            # create new external uploader without fetching user object from freesound
            external_uploader = SoundUploader.objects.create_freesound_uploader_min(sound_uploader_username)

        uploader = SoundUploader.objects.filter(external_user__username = external_uploader.external_user.username).first()
        
        default_user = User.objects.get(id=1)

        sound = self.create(
            internal_id = freesound_sound['id'],
            title=freesound_sound['name'],
            uploader=uploader,
            source='freesound',
            sound_type='background' if is_background else 'event',
            thumbnail=freesound_sound['images']['waveform_m'],
            duration=freesound_sound['duration'],
            loopable=1 if loopable else 0,
            url=freesound_sound['previews']['preview-lq-mp3'],
            is_downloaded=0
        )

        sound.save()

        for tag_string in tags:
            tag = Tag.objects.get_tag_from_string(tag_string)
            
            if not tag:
                tag = Tag.objects.create(default_user, tag_string)

            sound.tag.add(tag)

        sound.save()
        

        return sound
    
    def get_sound(self, sound_id):
        sound = self.filter(id=sound_id)
        
        if not sound.exists():
            return None

        return sound.first()
                


class Sound(models.Model):
    internal_id = models.IntegerField(default=0)
    title = models.CharField(max_length = 500)
    uploader = models.ForeignKey(SoundUploader, on_delete=models.CASCADE, related_name = 'uploaded_sounds', null=True)
    source = models.CharField(max_length=255)
    sound_type = models.CharField(max_length=255, default = 'event') # 'background' or 'event'
    is_downloaded = models.IntegerField(default = 0)
    thumbnail = models.CharField(max_length = 500, null = True, blank=True)

    tag = models.ManyToManyField(Tag, related_name = 'tagged_sounds')
    
    duration = models.FloatField()
    loopable = models.IntegerField(default = 0)
    url = models.CharField(max_length=500, null=True, blank=True)

    objects = SoundManager()

class Event(models.Model):
    sound = models.ForeignKey(Sound, on_delete=models.CASCADE, related_name = 'event_joined')
    event_index = models.IntegerField(default = 0)


class SoundScrollsJointManager(models.Manager):
    def create_joint(self, scrolls_id):
        scrolls = Scrolls.objects.get(id = scrolls_id)

        if not scrolls:
            return None
        
        joint = self.create(scrolls = scrolls)
        joint.save()

        return joint
    
    def add_background_sound(self, joint_id, sound_id):
        joint = self.get(id = joint_id)
        sound = Sound.objects.get(id = sound_id)
        
        if not sound or not joint:
            return None
        
        if sound.loopable == 0:
            return None
        
        joint.background = sound
        joint.save()

        return joint
    
    def add_event(self, joint_id, sound_id, event_index):
        joint = self.get(id = joint_id)
        sound = Sound.objects.get(id = sound_id)
        
        if not sound or not joint:
            return None
        
        event = Event.objects.create(sound = sound, event_index = event_index)
        event.save()
        joint.events.add(event)
        joint.save()

        return joint
        
class SoundScrollsJoint(models.Model):
    scrolls = models.ForeignKey(Scrolls, on_delete=models.CASCADE, related_name = 'sound_joints')
    background = models.ForeignKey(Sound, on_delete=models.CASCADE, related_name = 'background_joined', null=True, blank=True)
    events = models.ManyToManyField(Event, related_name = 'joint')

    objects = SoundScrollsJointManager()

    def get_background_sound(self):
        if not self.background:
            return None
        return self.background
    
    def get_event_sounds(self):
        if not self.events:
            return None
        return self.events.all()


    