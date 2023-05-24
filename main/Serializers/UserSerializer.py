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


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to login with provided credentials")