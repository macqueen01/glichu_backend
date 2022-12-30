import os

from django.db import models
from django.utils import timezone
from django.conf import settings
from .UserModel import User

from main import tasks
#from mockingJae_back.settings import

# Model Managers

class TagManager(models.Manager):

    def get_scrolls(self, tag_id):
        if (tag := self.filter(id__exact = tag_id)).exists():
            return tag.get().mentioned_in.all()
        return False

    def get_tag_name(self, tag_id):
        if (tag := self.filter(id__exact = tag_id)).exists():
            return tag.get().hashtag
        return False
    
    def get_tag_from_string(self, tag_string):
        if (tag := self.filter(hashtag__exact = tag_string)).exists():
            return tag.get()
        return False
    
    def create(self, user, tag_string):
        if not self.is_valid(tag_string):
            return False

        new_tag = self.model(
            hashtag = tag_string,
            created_at = timezone.now(),
            created_by = user
        ).save()

        return new_tag

    def is_valid(self, string):
        """
        Checks if given string is valid as a tag
        """
        if not isinstance(string, str):
            return False

        if len(string) == 0:
            return False

        if (' ' in string):
            return False
        
        if self.get_tag_from_string(string):
            return False
    

        # Needs profanity filter (both english and korean)
        return True

class VideoMediaManager(models.Manager):

    def get_video_from_id(self, media_id):
        if (media := self.filter(id__exact = media_id)).exists():
            return media.get()
        return False

    def convert(self, media_id):

        date = timezone.now().date().__str__().replace('-', '')

        #if self.is_media_converted(media_id):
        #    return False

        if (original_video := self.get_video_from_id(media_id)):
            converted_video_path = os.path.join(settings.MEDIA_ROOT, f'streams/video/{date}/{original_video.title}.mp4')
            original_video_path = original_video.url_preprocess
            encoding_task = tasks.convert.delay(input = original_video_path, output = converted_video_path, media_id = media_id)
            return encoding_task.id 
        return False

    def is_media_converted(self, media_id):
        media = self.get_video_from_id(media_id)
        if (media and media.url_postprocess):
            return True
        return False

    def mp4_to_scrolls(self, media_id, scrolls_id, fps=60, quality=5):

        date = timezone.now().date().__str__().replace('-', '')
        
        if not self.is_media_converted(media_id):
            return False
        
        if not Scrolls.objects.get_scrolls_from_id(scrolls_id):
            return False

        media = self.get_video_from_id(media_id)

        media_path = media.url_postprocess
        scrolls_path = os.path.join(settings.MEDIA_ROOT, f'scrolls/{date}/{media.title}/')

        if scrollify_task := tasks.scrollify.delay(input = media_path, output_dir = scrolls_path, fps = fps, quality = quality):
            return scrollify_task.id
        return False


class ScrollsManager(models.Manager):
    """
    Notion for the scrolls object:
    all methods implementing ScrollsManager are not meant to intervene
    video encoding and splicing. Those task-heavy actions are carried by
    VideoMediaManager.


    Workflow Overview:
    VID UPLOAD --> CONVERT --> CREATE SCROLLS --
                                                |
    UPLOAD_TO_IPFS    <--     MP4_TO_SCROLLS <--
    """

    def create(self, **kwargs):
        user = User.objects.get_user_from_id(kwargs['user_id'])
        media = VideoMedia.objects.get_video_from_id(kwargs['media_id'])

        if not media:
            return False

        new_scrolls = self.model(
            title = kwargs['title'],
            created_by = user,
            created_at = timezone.now(),
            original = media,
            height = kwargs['height']
        ).save()

        return new_scrolls
    
    def get_scrolls_from_id(self, scrolls_id):
        if (scrolls := self.filter(id__exact = scrolls_id)).exists():
            return scrolls.get()
        return False

    def create_cell(self, scrolls_id, hash):
        
        if scrolls := self.get_scrolls_from_id(scrolls_id):
            new_cell = Cell(
                url = f'https://ipfs.io/ipfs/{hash}'
            )

            new_cell.scrolls = scrolls
            new_cell.save()
            return new_cell

        return False
    
    def upload(self, scrolls_id, scrolls_dirname, wait=True):
        """
        Uploads the scroll cells to ipfs and returns 
        the uploaded scrolls object if wait == True,
        and returns the task_id if wait == False.
        """

        if not self.get_scrolls_from_id(scrolls_id):
            return False
        
        if not wait:
            upload_task = tasks.upload_to_ipfs(dirname=scrolls_dirname, scrolls_id=scrolls_id)
            return upload_task.id
        
        if upload_task_result := tasks.upload_to_ipfs(dirname=scrolls_dirname, scrolls_id=scrolls_id):
            # waits until the end of uploading
            return upload_task_result
        
        return False

    def is_scrolls_uploaded(self, scrolls_id):

        scrolls_object = self.get_scrolls_from_id(scrolls_id)
        
        if not scrolls_object:
            return False
        
        if not scrolls_object.uploaded:
            return False
        
        return True
             
    

# Models


class VideoMedia(models.Model):
    url_preprocess = models.FileField(upload_to='archive/video/%Y%m%d', default="")
    url_postprocess = models.TextField(default="")
    uploader = models.ForeignKey(to=User, on_delete=models.SET_NULL, default=None, related_name="uploaded_video", null=True)
    created_at = models.DateTimeField()
    title = models.CharField(max_length=400, default="Untitled")

    objects = VideoMediaManager()

    def __str__(self):
        return f'{self.id}'


class Tag(models.Model):
    hashtag = models.CharField(max_length=30, default="")
    created_by = models.ForeignKey(to=User, default=None, on_delete=models.DO_NOTHING, related_name="created_tags", null=True)
    created_at = models.DateTimeField()

    objects = TagManager()

    def __str__(self):
        return "#"+self.hashtag

    

class Scrolls(models.Model):
    title = models.CharField(max_length=100, default="Untitled")
    mention = models.ManyToManyField(to=User, related_name="mentioned_in")
    created_by = models.ForeignKey(to=User, on_delete=models.SET_NULL, default=None, related_name="uploaded_scrolls", null=True)
    created_at = models.DateTimeField()
    # CELLs will be url to each frame of uploaded scrolls form.
    # Take a look at the CELL model
    original = models.ForeignKey(to=VideoMedia, on_delete=models.SET_NULL, default=None, null=True)
    tags = models.ManyToManyField(to=Tag, related_name="mentioned_in")
    liked_by = models.ManyToManyField(to=User, related_name="likes")
    height = models.IntegerField(default=0)
    length = models.IntegerField(default=0)
    uploaded = models.IntegerField(default=0)

    objects = ScrollsManager()

    def __str__(self):
        return self.title


class Cell(models.Model):
    url = models.CharField(max_length=130, default="")
    scrolls = models.ForeignKey(to=Scrolls, related_name="cells", on_delete=models.CASCADE, null=True, default=None)
    