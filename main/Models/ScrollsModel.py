import os

from django.db import models
from django.utils import timezone
from django.conf import settings

from main.utils import create_tar_archive_with_parent_basename
from .UserModel import User

from main import tasks
from mockingJae_back.settings import s3_storage



from django.core.files.storage import FileSystemStorage

# Model Managers


class TagManager(models.Manager):

    def get_scrolls(self, tag_id):
        if (tag := self.filter(id__exact=tag_id)).exists():
            return tag.get().mentioned_in.all()
        return False

    def get_tag_name(self, tag_id):
        if (tag := self.filter(id__exact=tag_id)).exists():
            return tag.get().hashtag
        return False

    def get_tag_from_string(self, tag_string):
        if (tag := self.filter(hashtag__exact=tag_string)).exists():
            return tag.get()
        return False

    def create(self, user, tag_string):
        if not self.is_valid(tag_string):
            return False

        new_tag = self.model(
            hashtag=tag_string,
            created_at=timezone.now(),
            created_by=user
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

    def create(self, **kwargs):
        """
        Create method does not implement video converting.
        This leaves URL_POSTPROCESS attribute unset during the creation.
        Make sure to set URL_POSTPROCESS after video conversion.

        create should get following argument, and they are mendatory.

        @ video - original file object (request.FILE)
        @ user_id - user id of the user sending the request
        @ title - title of the video
        """
        try:
            url_preprocess = kwargs['video']
            uploader = User.objects.get_user_from_id(kwargs['user_id'])
            title = kwargs['title']
            created_at = timezone.now()

            media_object = self.model(
                url_preprocess=url_preprocess,
                uploader=uploader,
                created_at=created_at,
                title=title
            )

            media_object.save()
            return media_object
        except:
            return False
    
    def delete(self, media_id):
        media = self.get_video_from_id(media_id)

        if not media:
            return False
        
        os.remove(media.url_preprocess)
        media.delete()

        return True

    def complete_delete(self, media_id):
        media = self.get_video_from_id(media_id)

        if not media:
            return False
        
        if self.is_media_converted(media_id):
            os.remove(media.url_postprocess)
        
        os.remove(media.url_preprocess)
        media.delete()

        return True

        

    def get_video_from_id(self, media_id):
        if (media := self.filter(id__exact=media_id)).exists():
            return media.get()
        return False

    def convert(self, media_id):

        date = timezone.now().date().__str__().replace('-', '')

        #if self.is_media_converted(media_id):
        #    return False

        if (original_video := self.get_video_from_id(media_id)):
            converted_video_path = os.path.join(
                settings.MEDIA_ROOT, f'streams/video/{date}/{original_video.title}.mp4')
            original_video_path = os.path.join(settings.MEDIA_ROOT, original_video.url_preprocess.__str__())
            encoding_task = tasks.convert.delay(
                input=original_video_path, output=converted_video_path, media_id=media_id)
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
        scrolls_path = os.path.join(
            settings.MEDIA_ROOT, f'scrolls/{date}/{media.title}/')

        if scrollify_task := tasks.scrollify.delay(input=media_path, output_dir=scrolls_path, fps=fps, quality=quality):
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
        media = VideoMedia.objects.get_video_from_id(kwargs['media_id'])
        user = media.uploader

        if not media:
            return False

        new_scrolls = self.model(
            title=kwargs['title'],
            created_by=user,
            created_at=timezone.now(),
            original=media,
            height=kwargs['height']
        )
        new_scrolls.save()

        return new_scrolls

    def delete(self, scrolls_id):
        """
        If a scroll is deleted, the original 
        VideoMedia is deleted as a whole.
        """
        scrolls = self.get_scrolls_from_id(scrolls_id)
        
        if not scrolls:
            return False
        
        VideoMedia.objects.delete(scrolls.original.id)

        return True        

        

    def get_scrolls_from_id(self, scrolls_id):
        if (scrolls := self.filter(id__exact=scrolls_id)).exists():
            return scrolls.get()
        return False

    def create_cell(self, scrolls_id, hash, index):

        if scrolls := self.get_scrolls_from_id(scrolls_id):
            new_cell = Cell(
                url=f'https://ipfs.io/ipfs/{hash}',
                index=index
            )

            new_cell.scrolls = scrolls
            new_cell.save()
            return new_cell

        return False

    def _upload_to_s3(self, scrolls_id, scrolls_dirname):
        """
        Only used inside the manager.
        Should not be called from outside.
        """

        scrolls_to_be_uploaded = self.get_scrolls_from_id(scrolls_id)

        if not scrolls_to_be_uploaded:
            return False

        destination = f'{scrolls_dirname}/id{scrolls_to_be_uploaded.id}.tar'

        create_tar_archive_with_parent_basename(
            scrolls_dirname,
            destination,
            parent_basename = self.parsed_scrolls_name(scrolls_id))
        
        with open(destination, 'rb') as f:
            file_data = f.read()
        
        try:
            result = s3_storage.save(f'scrolls/id{scrolls_to_be_uploaded.id}.tar', file_data)
        except:
            return False
            
        return result

    def upload(self, scrolls_id, scrolls_dirname, wait=True, ipfs=True):
        """
        Uploads the scroll cells to ipfs and returns 
        the uploaded scrolls object if wait == True,
        and returns the task_id if wait == False.
        """

        if not self.get_scrolls_from_id(scrolls_id):
            return False

        if not ipfs:
            # handles upload to 
            return self._upload_to_s3(scrolls_id, scrolls_dirname, wait=wait)

        if not wait:
            upload_task = tasks.upload_to_ipfs_as_a_directory.delay(
                dirname=scrolls_dirname, scrolls_id=scrolls_id)
            return upload_task.id

        if upload_task_result := tasks.upload_to_ipfs_as_a_directory(dirname=scrolls_dirname, scrolls_id=scrolls_id):
            # waits until the end of uploading
            return upload_task_result

        return False


    def parsed_scrolls_name(self, scrolls_id):
        # returns a name that can be used for uploading scrolls to s3
        scrolls = self.get_scrolls_from_id(scrolls_id)

        if not scrolls:
            return False
        
        parsed_name = scrolls.id + '_' + scrolls.title.replace(' ', '_') + '/scrolls' # "<id>_<scrolls title without whitespace>/scrolls"
        return parsed_name

    def initialize(self, scrolls_id):
        """
        Initializes cells and length.
        This should be called inside UPLOAD_TO_IPFS 
        to make sure no remaining cells are inside scrolls before 
        adding cells to scrolls.

        Always returns True (bool)
        """

        if not self.is_scrolls_uploaded(scrolls_id):
            return None

        scrolls = self.get_scrolls_from_id(scrolls_id)
        scrolls.cells.remove(*scrolls.cells.all())
        scrolls.length = 0
        return None

    def is_scrolls_uploaded(self, scrolls_id):

        scrolls_object = self.get_scrolls_from_id(scrolls_id)

        if not scrolls_object:
            return False

        if not scrolls_object.uploaded:
            return False

        return True



    """
    
    # scrolls recommendation from interest
    def get_recommended_scrolls(self, user_id):
        user = User.objects.get_user_from_id(user_id)
        if not user:
            return False

        if not user.interests.exists():
            return False

        interests = user.interests.all()
        scrolls = Scrolls.objects.all()

        for interest in interests:
            scrolls = scrolls.filter(tags__hashtag__icontains=interest.hashtag)

        return scrolls

# History model manager class.
# This model manager updates the interest of the user by calculating 
# user-watched scrolls hashtags.
class HistoryManager(models.Manager):

    def create(self, **kwargs):
        user = User.objects.get_user_from_id(kwargs['user_id'])
        scrolls = Scrolls.objects.get_scrolls_from_id(kwargs['scrolls_id'])

        if not user or not scrolls:
            return False

        new_history = self.model(
            user=user,
            scrolls=scrolls,
            created_at=timezone.now()
        )

        new_history.save()
        return new_history

    def delete(self, history_id):
        if not self.get_history_from_id(history_id):
            return False

        self.filter(id__exact=history_id).delete()
        return True

    def get_history_from_id(self, history_id):
        if (history := self.filter(id__exact=history_id)).exists():
            return history.get()
        return False

    def get_history_from_user(self, user_id):
        if not User.objects.get_user_from_id(user_id):
            return False

        if (histories := self.filter(user__id__exact=user_id)).exists():
            return histories

        return False

    def get_history_from_scrolls(self, scrolls_id):
        if not Scrolls.objects.get_scrolls_from_id(scrolls_id):
            return False

        if (histories := self.filter(scrolls__id__exact=scrolls_id)).exists():
            return histories

        return False

    def get_history_from_user_and_scrolls(self, user_id, scrolls_id):
        if not User.objects.get_user_from_id(user_id):
            return False

        if not Scrolls.objects.get_scrolls_from_id(scrolls_id):
            return False

        if (histories := self.filter(user__id__exact=user_id, scrolls__id__exact=scrolls_id)).exists():
            return histories.get()

        return False

    def update_interest(self, user_id):
        if not User.objects.get_user_from_id(user_id):
            return False

        if not (histories := self.get_history_from_user(user_id)):
            return False

        user = User.objects.get_user_from_id(user_id)
        user.interests.remove(*user.interests.all())

        for history in histories:
            for tag in history.scrolls.tags.all():
                if not user.interests.filter(hashtag__exact=tag.hashtag).exists():
                    user.interests.add(tag)

        return True

"""


# Models



class VideoMedia(models.Model):
    url_preprocess = models.FileField(
        upload_to='archive/video/%Y%m%d', default="")
    url_postprocess = models.TextField(default="", null=True)
    uploader = models.ForeignKey(to=User, on_delete=models.SET_NULL,
                                 default=None, related_name="uploaded_video", null=True)
    created_at = models.DateTimeField()
    title = models.CharField(max_length=400, default="Untitled")

    objects = VideoMediaManager()

    def __str__(self):
        return f'{self.id}'


class Tag(models.Model):
    hashtag = models.CharField(max_length=30, default="")
    created_by = models.ForeignKey(
        to=User, default=None, on_delete=models.DO_NOTHING, related_name="created_tags", null=True)
    created_at = models.DateTimeField()

    objects = TagManager()

    def __str__(self):
        return "#"+self.hashtag


class Scrolls(models.Model):
    title = models.CharField(max_length=100, default="Untitled")
    mention = models.ManyToManyField(to=User, related_name="mentioned_in")
    created_by = models.ForeignKey(
        to=User, on_delete=models.SET_NULL, default=None, related_name="uploaded_scrolls", null=True)
    created_at = models.DateTimeField()
    # CELLs will be url to each frame of uploaded scrolls form.
    # Take a look at the CELL model
    original = models.ForeignKey(
        to=VideoMedia, on_delete=models.SET_NULL, default=None, null=True)
    tags = models.ManyToManyField(to=Tag, related_name="mentioned_in")
    liked_by = models.ManyToManyField(to=User, related_name="likes")
    height = models.IntegerField(default=0)
    length = models.IntegerField(default=0)
    uploaded = models.IntegerField(default=0)
    # Hash of ipfs if uploaded as a folder
    # This could be empty if scrolls is uploaded as a cell
    ipfs_hash = models.CharField(max_length=100, default="")

    objects = ScrollsManager()

    def __str__(self):
        return self.title


class Cell(models.Model):
    url = models.CharField(max_length=130, default="")
    index = models.IntegerField(default=0)
    scrolls = models.ForeignKey(
        to=Scrolls, related_name="cells", on_delete=models.CASCADE, null=True, default=None)

    def __str__(self):
        return self.index.__str__()



"""
class History(models.Model):

    #History of the user scrolls watching.
    #Used by algorithm to recommend scrolls.


    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="history")
    scrolls = models.ForeignKey(
        to=Scrolls, on_delete=models.CASCADE, related_name="history")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} - {self.scrolls.title}'

    class Meta:
        unique_together = ('user', 'scrolls')
"""


