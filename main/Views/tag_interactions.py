from django.utils import timezone
import requests

from knox.models import AuthToken
from knox.settings import CONSTANTS

from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.pagination import PageNumberPagination
from main.Views.authentications import authenticate_then_user_or_unauthorized_error, authenticate_and_invitation_check_then_user_or_unauthorized_error

from main.models import Scrolls, User, Recommendation
from main.serializer import *


def has_tagged(request, target_id):
    user = authenticate_then_user_or_unauthorized_error(request)

    if request.method != 'GET':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    if User.objects.get(id=target_id) is None:
        return Response({'message': 'user is invalid'}, status=status.HTTP_400_BAD_REQUEST)
    
    """
    if user.id == target_id:
        return Response({'message': 'cannot invite yourself'}, status=status.HTTP_400_BAD_REQUEST)
    """
    if user.invited.filter(id=target_id).exists():
        return Response({'has_tagged': 1}, status=status.HTTP_200_OK)
    
    return Response({'has_tagged': 0}, status=status.HTTP_200_OK)



def accept_invitation(request, inviter_id):
    user = authenticate_then_user_or_unauthorized_error(request)

    if request.method != 'POST':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    if User.objects.get(id=inviter_id) is None:
        return Response({'message': 'user is invalid'}, status=status.HTTP_400_BAD_REQUEST)
    
    """
    if user.id == target_id:
        return Response({'message': 'cannot accept invitation from yourself'}, status=status.HTTP_400_BAD_REQUEST)
    """

    if user.invited_by.filter(id=inviter_id).exists():
        return Response({'message': 'invitation already accepted'}, status=status.HTTP_400_BAD_REQUEST)
    
    result = User.objects.accept_invitation(user.id, inviter_id)

    if result == 0:
        return Response({'message': 'invitation error'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'invitation accepted'}, status=status.HTTP_200_OK)
    

