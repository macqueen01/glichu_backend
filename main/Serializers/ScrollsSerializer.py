from rest_framework import serializers
from ..models import *
from .UserSerializer import UserSerializer

class MediaSerializer(serializers.ModelSerializer):
    url_preprocess = serializers.FileField()
    url_postprocess = serializers.CharField()
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
    index = serializers.IntegerField()
    
    class Meta:
        model = Cell
        fields = (
            'index',
            'url'
        )

class ScrollsSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    mention = UserSerializer(many=True)
    created_by = UserSerializer()
    created_at = serializers.DateTimeField()
    tags = TagSerializer(many=True)
    liked_by = UserSerializer(many = True)
    height = serializers.IntegerField()
    length = serializers.IntegerField()
    cells = serializers.SerializerMethodField()
    uploaded = serializers.IntegerField()
    ipfs_hash = serializers.CharField(max_length=100)
    scrolls_url = serializers.CharField(max_length=400)

    def get_cells(self, instance):
        queryset = instance.cells.order_by('index')
        return CellSerializer(queryset, many=True).data

    class Meta:
        model = Scrolls
        fields = (
            'id',
            'title',
            'mention',
            'created_by',
            'created_at',
            'tags',
            'liked_by',
            'height',
            'length',
            'cells',
            'uploaded',
            'ipfs_hash',
            'scrolls_url'
        )

    

    




