import json
from rest_framework import serializers
from main.models import Remix, User, Scrolls
from main.Serializers.UserSerializer import UserSerializerForRemix
from main.Serializers.ScrollsSerializer import ScrollsSerializerForRemix

class RemixViewSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255)
    user = UserSerializerForRemix()
    scrolls = ScrollsSerializerForRemix()
    thumbnail_url = serializers.SerializerMethodField()

    def get_thumbnail_url(self, instance):
        media = instance.scrolls.original
        if thumbnail := media.thumbnail:
            return thumbnail.url.split('?')[0]
        return f'{instance.scrolls.scrolls_dir}/1.jpeg'

    class Meta:
        model = Remix
        fields = (
            'id',
            'title',
            'user',
            'scrolls',
            'thumbnail_url'
        )

class RemixViewSerializerWithRawJson(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255)
    user = UserSerializerForRemix()
    scrolls = ScrollsSerializerForRemix()
    thumbnail_url = serializers.SerializerMethodField()
    timeline = serializers.SerializerMethodField()
    length = serializers.SerializerMethodField()
    scrolls_video_url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    
    is_liked_by_user = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()

    def get_thumbnail_url(self, instance):
        media = instance.scrolls.original
        if thumbnail := media.thumbnail:
            return thumbnail.url.split('?')[0]
        return f'{instance.scrolls.scrolls_dir}/1.jpeg'
    
    def get_timeline(self, obj):
        remix_json_string = obj.task_queue_json.replace('/', '')
        timeline = json.loads(remix_json_string)['timeline']
        return timeline
    
    def get_length(self, obj):
        remix_json_string = obj.task_queue_json.replace('/', '')
        length = json.loads(remix_json_string)['length']
        return length
    
    def get_scrolls_video_url(self, obj):
        scrolls = Scrolls.objects.get(id=obj.scrolls.id)
        scrolls_video_url = scrolls.video_url
        return scrolls_video_url
    
    def get_is_liked_by_user(self, obj):
        user = self.context.get('user')
        
        if user in obj.liked_by.all():
            return 1
        
        return 0

    def get_likes(self, obj):
        return obj.liked_by.count()

    class Meta:
        model = Remix
        fields = (
            'id',
            'title',
            'user',
            'scrolls',
            'thumbnail_url',
            'timeline',
            'length',
            'scrolls_video_url',
            'created_at',
            'is_liked_by_user',
            'likes'
        )