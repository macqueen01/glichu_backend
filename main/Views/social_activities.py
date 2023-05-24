from django.utils import timezone
import requests

from knox.models import AuthToken
from knox.settings import CONSTANTS

from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.pagination import PageNumberPagination
from main.Views.authentications import authenticate_then_user_or_unauthorized_error

from main.models import Scrolls, User, Recommendation
from main.serializer import *


def get_user(request, user_id):
    user = authenticate_then_user_or_unauthorized_error(request)

    if request.method != 'GET':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    target_user = User.objects.get_user_from_id(user_id)

    if (target_user is None):
        return Response({'message': 'user is invalid'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserSerializerWithFollowingRelations(target_user)
    return Response(serializer.data, status=status.HTTP_200_OK)


def follow(request):
    user = authenticate_then_user_or_unauthorized_error(request)

    if request.method != 'POST':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    try:
        target = request.data['target_id']
        User.objects.follow_user_from_id(user.id, target)
        return Response({'message': 'followed'}, status=status.HTTP_200_OK)
    except:
        return Response({'message': 'argument missing'}, status=status.HTTP_400_BAD_REQUEST)
    

def unfollow(request):
    user = authenticate_then_user_or_unauthorized_error(request)

    if request.method != 'POST':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    try:
        target = request.data['target_id']
        User.objects.unfollow_user_from_id(user.id, target)
        return Response({'message': 'unfollowed'}, status=status.HTTP_200_OK)
    except:
        return Response({'message': 'argument missing'}, status=status.HTTP_400_BAD_REQUEST)
    

def get_followers(request, user_id):
    user = authenticate_then_user_or_unauthorized_error(request)

    if request.method != 'GET':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    try:
        followers = User.objects.get_followers(user_id).order_by('username')
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(followers, request)
        serializer = UserSerializerWithFollowingRelations(result_page, context={'user': user}, many=True)
        return paginator.get_paginated_response(serializer.data)
    except:
        return Response({'message': 'argument missing'}, status=status.HTTP_400_BAD_REQUEST)
    
def get_followings(request, user_id):
    user = authenticate_then_user_or_unauthorized_error(request)

    if request.method != 'GET':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    try:
        followings = User.objects.get_followings(user_id).order_by('username')
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(followings, request)
        serializer = UserSerializerWithFollowingRelations(result_page, context={'user': user}, many=True)
        return paginator.get_paginated_response(serializer.data)
    except:
        return Response({'message': 'argument missing'}, status=status.HTTP_400_BAD_REQUEST)
    

