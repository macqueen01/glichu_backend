from django.utils import timezone
import requests

from knox.models import AuthToken
from knox.settings import CONSTANTS

from rest_framework.response import Response
from rest_framework import status, exceptions

from channels.db import database_sync_to_async

from main.models import Scrolls, User, Recommendation
from main.serializer import *

from asgiref.sync import sync_to_async




def get_token_from_request(request):
    try: 
        _, token = request.META.get('HTTP_AUTHORIZATION').split(' ')
        return token
    except:
        return None
    

def get_user_from_token(token):
    objs = AuthToken.objects.filter(token_key=token[:CONSTANTS.TOKEN_KEY_LENGTH])
    if len(objs) == 0:
        return None
    return objs.first().user


def authenticate_then_user_or_unauthorized_error(request):

    if token := get_token_from_request(request):
        user = get_user_from_token(token)
        return user
    else:
        raise exceptions.AuthenticationFailed('token is invalid', code=status.HTTP_401_UNAUTHORIZED)

def authenticate_and_invitation_check_then_user_or_unauthorized_error(request):

    user = authenticate_then_user_or_unauthorized_error(request)

    if user.is_invited == 1:
        return user
    # This will ensure user is authenticated, but without invitation
    return Response({'message': 'user is not invited', 'invitation': 0}, status=status.HTTP_200_OK)

    

async def authenticate_then_user_or_none_for_websocket(websocket_scope):
    if token := dict(websocket_scope['headers']).get(b'sec-websocket-protocol', None):
        token = token.decode('utf-8')
        user = await database_sync_to_async(get_user_from_token)(token)
        return user
    return None