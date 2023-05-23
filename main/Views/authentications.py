from django.utils import timezone
import requests

from knox.models import AuthToken
from knox.settings import CONSTANTS

from rest_framework.response import Response
from rest_framework import status, exceptions

from main.models import Scrolls, User, Recommendation
from main.serializer import *




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
        return Response({'message': 'token is invalid'}, status=status.HTTP_401_UNAUTHORIZED)