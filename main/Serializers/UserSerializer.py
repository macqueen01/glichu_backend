from rest_framework import serializers
from main.models import *
from django.contrib.auth import authenticate


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "username",
            "password",
        )

        extra_kwargs = {'password': {"write_only": True}}


    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "created_at",
            "is_staff",
            "is_active"
        )


class UserSerializerForRemix(serializers.ModelSerializer):
    profile_image = serializers.ImageField(use_url=True)
    tagged_by = serializers.SerializerMethodField()
    is_tagged = serializers.SerializerMethodField()

    def get_tagged_by(self, obj):
        
        if not obj.invited_by.exists():
            return 'Tagger not found'
        
        tagger = obj.invited_by.all().last()
        
        return tagger.username
    
    def get_is_tagged(self, obj):
        if obj.is_invited == 1:
            return 1
        return 0

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "profile_image",
            "tagged_by",
            "is_tagged",
            "influencer"
        )

class UserSerializerForScrolls(serializers.ModelSerializer):
    profile_image = serializers.ImageField(use_url=True)
    tagged_by = serializers.SerializerMethodField()
    is_tagged = serializers.SerializerMethodField()

    def get_tagged_by(self, obj):
        
        if not obj.invited_by.exists():
            return 'Tagger not found'
        
        tagger = obj.invited_by.all().last()
        
        return tagger.username
    
    def get_is_tagged(self, obj):
        if obj.is_invited == 1:
            return 1
        return 0

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "profile_image",
            "tagged_by",
            "is_tagged",
            "influencer"
        )

class UserSerializerGeneralUse(serializers.ModelSerializer):
    profile_image = serializers.ImageField(use_url=True)
    tagged_by = serializers.SerializerMethodField()
    is_tagged = serializers.SerializerMethodField()

    def get_tagged_by(self, obj):
        
        if not obj.invited_by.exists():
            return 'Tagger not found'
        
        tagger = obj.invited_by.all().last()
        
        return tagger.username
    
    def get_is_tagged(self, obj):
        if obj.is_invited == 1:
            return 1
        return 0

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "profile_image",
            "tagged_by",
            "is_tagged",
            "influencer"
        )

class UserSerializerWithFollowingRelations(serializers.ModelSerializer):
    is_followed_by_user = serializers.SerializerMethodField()
    is_following_user = serializers.SerializerMethodField()
    profile_image = serializers.ImageField(use_url=True)
    tagged_by = serializers.SerializerMethodField()
    is_tagged = serializers.SerializerMethodField()
    
    def get_is_followed_by_user(self, obj):
        user = self.context.get("user")
        return obj.followers.filter(pk=user.id).exists()

    def get_is_following_user(self, obj):
        user = self.context.get("user")
        return obj.followings.filter(pk=user.id).exists()
    
    def get_tagged_by(self, obj):
        
        if not obj.invited_by.exists():
            return 'Tagger not found'
        
        tagger = obj.invited_by.all().last()
        
        return tagger.username
    
    def get_is_tagged(self, obj):
        if obj.is_invited == 1:
            return 1
        return 0
    
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "profile_image",
            "is_followed_by_user",
            "is_following_user",
            "tagged_by",
            "is_tagged",
            "influencer"
        )


class UserSerializerWithDetail(serializers.ModelSerializer):
    profile_image = serializers.ImageField(use_url=True)
    num_followers = serializers.SerializerMethodField()
    num_followings = serializers.SerializerMethodField()
    num_scrolls_uploaded = serializers.SerializerMethodField()
    num_scrolls_scrolled = serializers.SerializerMethodField()
    num_remix_produced = serializers.SerializerMethodField()
    tagged_by = serializers.SerializerMethodField()
    is_tagged = serializers.SerializerMethodField()
    is_followed_by_user = serializers.SerializerMethodField()
    is_following_user = serializers.SerializerMethodField()
    invited_by = serializers.SerializerMethodField()
    invited_at = serializers.SerializerMethodField()


    def get_is_followed_by_user(self, obj):
        user = self.context.get("user")
        return obj.followers.filter(pk=user.id).exists()
    
    def get_is_following_user(self, obj):
        user = self.context.get("user")
        return obj.followings.filter(pk=user.id).exists()
    

    def get_num_followers(self, obj):
        return len(obj.followers.all()) 
    
    def get_num_followings(self, obj):
        return len(obj.followings.all()) 
    
    def get_num_scrolls_uploaded(self, obj):
        return len(obj.uploaded_scrolls.exclude(video_url = '/'))
    
    
    def get_num_scrolls_scrolled(self, obj):
        total_scrolled = 0
        for scrolls in obj.uploaded_scrolls.exclude(video_url = '/'):
            total_scrolled += scrolls.scrolled
        
        return total_scrolled
    
    def get_num_remix_produced(self, obj):
        return len(obj.remix_set.all())
    
    def get_tagged_by(self, obj):
        
        if not obj.invited_by.exists():
            return 'Tagger not found'
        
        tagger = obj.invited_by.all().last()
        
        return tagger.username
    
    def get_is_tagged(self, obj):
        if obj.is_invited == 1:
            return 1
        return 0
    
    def get_invited_at(self, obj):
        if not obj.invited_at:
            return None
        
        time = obj.invited_at
        return time
    
    def get_invited_by(self, obj):
        if not obj.invited_by.exists():
            return None
        
        tagger = obj.invited_by.all().first()
        tagger_result = UserSerializerGeneralUse(tagger).data
        return tagger_result

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "profile_image",
            "is_followed_by_user",
            "is_following_user",
            "num_followers",
            "num_followings",
            "num_scrolls_uploaded",
            "num_scrolls_scrolled",
            "num_remix_produced",
            "tagged_by",
            "is_tagged",
            "invited_by",
            "invited_at",
            "influencer"
        )


class UserSerializerForSelfProfile(serializers.ModelSerializer):
    profile_image = serializers.ImageField(use_url=True)
    num_followers = serializers.SerializerMethodField()
    num_followings = serializers.SerializerMethodField()
    num_scrolls_uploaded = serializers.SerializerMethodField()
    num_scrolls_scrolled = serializers.SerializerMethodField()
    num_remix_produced = serializers.SerializerMethodField()
    tagged_by = serializers.SerializerMethodField()
    is_tagged = serializers.SerializerMethodField()

    def get_num_followers(self, obj):
        return len(obj.followings.all()) 
    
    def get_num_followings(self, obj):
        return len(obj.followings.all()) 
    
    def get_num_scrolls_uploaded(self, obj):
        return len(obj.uploaded_scrolls.exclude(video_url = '/'))
    
    
    def get_num_scrolls_scrolled(self, obj):
        total_scrolled = 0
        for scrolls in obj.uploaded_scrolls.exclude(video_url = '/'):
            total_scrolled += scrolls.scrolled
        
        return total_scrolled
    
    def get_num_remix_produced(self, obj):
        return len(obj.remix_set.all())
    
    def get_tagged_by(self, obj):
        
        if not obj.invited_by.exists():
            return 'Tagger not found'
        
        tagger = obj.invited_by.all().last()
        
        return tagger.username
    
    def get_is_tagged(self, obj):
        if obj.is_invited == 1:
            return 1
        return 0
    
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "profile_image",
            "num_followers",
            "num_followings",
            "num_scrolls_uploaded",
            "num_scrolls_scrolled",
            "num_remix_produced",
            "tagged_by",
            "is_tagged",
            "influencer"
        )
    




class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to login with provided credentials")