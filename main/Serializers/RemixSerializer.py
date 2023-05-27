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

    def get_thumbnail_url(self, instance):
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
            'created_at'
        )