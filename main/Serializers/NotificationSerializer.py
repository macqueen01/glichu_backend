import json
from rest_framework import serializers
from main.models import Remix, User, Scrolls
from main.Serializers.UserSerializer import UserSerializerForRemix, UserSerializerGeneralUse, UserSerializerWithFollowingRelations
from main.Serializers.ScrollsSerializer import ScrollsSerializerForRemix

from notifications.models import Notification

class NotificationSerializerGeneralUse(serializers.ModelSerializer):
    id = serializers.IntegerField()
    recipient_id = serializers.IntegerField()
    actor = UserSerializerGeneralUse()
    timestamp = serializers.DateTimeField()
    verb = serializers.CharField()
    

    unread = serializers.SerializerMethodField()
    deleted = serializers.SerializerMethodField()


    def get_unread(self, obj):
        if obj.unread:
            return 1
        return 0
    
    def get_deleted(self, obj):
        if obj.deleted:
            return 1
        return 0
    

    class Meta:
        model = Notification
        fields = [
            'id',
            'recipient_id',
            'actor',
            'timestamp',
            'verb',
            'unread',
            'deleted'
            
        ]

    
