from rest_framework import serializers
from main.models import *
from UserSerializer import UserSerializer

class MediaSerializer(serializers.ModelSerializer):
    url_preprocess = serializers.FileField()
    url_postprocess = serializers.TextField()
    uploader = UserSerializer()
    created_at = serializers.DateTimeField()
    title = serializers.CharField(max_length=400)

    class Meta:
        model = VideoMedia
        fields = (
            'id',
            'url_preprocess',
            'url_postprocess',
            'uploader',
            'created_at',
            'title'
        )

class TagSerializer(serializers.ModelSerializer):
    hashtag = serializers.CharField(max_length=30)
    created_by = UserSerializer()
    created_at = serializers.DateTimeField()

    class Meta:
        model = Tag
        fields = (
            'id',
            'hashtag',
            'created_by',
            'created_at'
        )

class CellSerializer(serializers.ModelSerializer):
    url = serializers.CharField(max_length=130)
    
    class Meta:
        model = Cell
        field = (
            'id',
            'url'
        )

class ScrollsSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    mention = UserSerializer()
    created_by = UserSerializer()
    created_at = serializers.DateTimeField()
    original = MediaSerializer()
    tags = TagSerializer()
    liked_by = UserSerializer()
    height = serializers.IntegerField()
    length = serializers.IntegerField()
    cells = CellSerializer()

    class Meta:
        model = Scrolls
        fields = (
            'id',
            'title',
            'mention',
            'created_by',
            'original',
            'tags',
            'liked_by',
            'height',
            'length',
            'cells'
        )
    




