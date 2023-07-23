from rest_framework import serializers
from main.Serializers.UserSerializer import UserSerializerGeneralUse
from main.models import Sound





class SoundSerializerForSearchView(serializers.ModelSerializer):
    title = serializers.CharField(max_length=500)
    source = serializers.CharField(max_length=200)
    sound_type = serializers.CharField(max_length=255)
    thumbnail = serializers.CharField(max_length=500)
    duration = serializers.FloatField()
    loopable = serializers.IntegerField()
    url = serializers.CharField(max_length=500)

    user = serializers.SerializerMethodField()


    def get_user(self, object):

        uploader = object.uploader

        if uploader.is_internal:
            return UserSerializerGeneralUse(uploader.internal_user)

        return {
            'id': object.uploader.external_user.id,
            'source': object.source,
            'username': object.uploader.external_user.username,
            'profile_image': object.uploader.external_user.profile_image,
            'profile_url': object.uploader.external_user.profile_url
        }

    class Meta:
        model = Sound
        fields = (
            'id',
            'title',
            'source',
            'sound_type',
            'thumbnail',
            'duration',
            'loopable',
            'url',
            'user'
        )

class EventSerializer(serializers.ModelSerializer):
    sound = SoundSerializerForSearchView()
    event_index = serializers.IntegerField()

    class Meta:
        model = Sound
        fields = (
            'sound',
            'event_index'
        )


class SoundScrollsJointSerializerForScrolls(serializers.ModelSerializer):
    background = SoundSerializerForSearchView()
    events = EventSerializer(many=True)

    class Meta:
        model = Sound
        fields = (
            'id',
            'background',
            'events'
        )


