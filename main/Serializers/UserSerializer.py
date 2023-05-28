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

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "profile_image"
        )

class UserSerializerForScrolls(serializers.ModelSerializer):
    profile_image = serializers.ImageField(use_url=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "profile_image"
        )

class UserSerializerGeneralUse(serializers.ModelSerializer):
    profile_image = serializers.ImageField(use_url=True)
    

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "profile_image"
        )

class UserSerializerWithFollowingRelations(serializers.ModelSerializer):
    is_followed_by_user = serializers.SerializerMethodField()
    is_following_user = serializers.SerializerMethodField()
    profile_image = serializers.ImageField(use_url=True)
    
    def get_is_followed_by_user(self, obj):
        user = self.context.get("user")
        return obj.followers.filter(pk=user.id).exists()

    def get_is_following_user(self, obj):
        user = self.context.get("user")
        return obj.followings.filter(pk=user.id).exists()
    
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "profile_image",
            "is_followed_by_user",
            "is_following_user"
        )


class UserSerializerForSelfProfile(serializers.ModelSerializer):
    profile_image = serializers.ImageField(use_url=True)
    num_followers = serializers.SerializerMethodField()
    num_followings = serializers.SerializerMethodField()
    num_scrolls_uploaded = serializers.SerializerMethodField()
    num_scrolls_scrolled = serializers.SerializerMethodField()
    num_remix_produced = serializers.SerializerMethodField()
    tagged_by = serializers.SerializerMethodField()

    def get_num_followers(self, obj):
        return len(obj.followings.all()) - 1
    
    def get_num_followings(self, obj):
        return len(obj.followings.all()) - 1
    
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
        tagger = obj.tagger

        if (tagger == None):
            return 'Tagger not found'
        
        return tagger.username
    




class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to login with provided credentials")