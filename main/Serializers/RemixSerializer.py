from rest_framework import serializers
from main.models import Remix, User, Scrolls
from main.Serializers.UserSerializer import UserSerializerForRemix
from main.Serializers.ScrollsSerializer import ScrollsSerializerForRemix

class RemixViewSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255)
    user = UserSerializerForRemix()
    remix_directory = serializers.CharField(max_length=500)
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
            'remix_directory',
            'scrolls',
            'thumbnail_url'
        )