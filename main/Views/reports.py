import json
from django.utils import timezone
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.pagination import PageNumberPagination

from notifications.signals import notify

from main.BusinessLogics.Authentications.instagram_authentication import get_user_from_token
from main.BusinessLogics.Scrolls.timelines import IndexTimeline
from main.BusinessLogics.Scrolls.timelines import Remix as RemixInMemory
from main.Views.authentications import authenticate_then_user_or_unauthorized_error


from main.models import Scrolls, User, Remix
from main.serializer import *
from main import tasks

def raise_scrolls_report(request, scrolls_id):
    user = authenticate_then_user_or_unauthorized_error(request)

    if (request.method != 'POST'):
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    if not user:
        return Response({'message': 'user not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    scrolls = Scrolls.objects.get(id=scrolls_id)

    if not scrolls:
        return Response({'message': 'scrolls not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    if scrolls.created_by == user:
        return Response({'message': 'cannot report your own scrolls'},
            status=status.HTTP_400_BAD_REQUEST)
    
    Scrolls.objects.raise_scrolls_report(user.id, scrolls.id)

    return Response({'message': 'success'}, status=status.HTTP_200_OK)

def raise_remix_report(request, remix_id):
    user = authenticate_then_user_or_unauthorized_error(request)

    if (request.method != 'POST'):
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    if not user:
        return Response({'message': 'user not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    remix = Remix.objects.get(id=remix_id)

    if not remix:
        return Response({'message': 'remix not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    if remix.created_by == user:
        return Response({'message': 'cannot report your own remix'},
            status=status.HTTP_400_BAD_REQUEST)
    
    Remix.objects.raise_remix_report(user.id, remix.id)

    return Response({'message': 'success'}, status=status.HTTP_200_OK)

def raise_user_report(request, user_id):
    user = authenticate_then_user_or_unauthorized_error(request)

    if (request.method != 'POST'):
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    if not user:
        return Response({'message': 'user not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    user_reported = User.objects.get(id=user_id)

    if not user_reported:
        return Response({'message': 'user not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    
    if user_reported == user:
        return Response({'message': 'cannot report yourself'},
            status=status.HTTP_400_BAD_REQUEST)
    
    User.objects.raise_user_report(user.id, user_reported.id)

    return Response({'message': 'success'}, status=status.HTTP_200_OK)

def get_scrolls_report_by_user(request):
    user = authenticate_then_user_or_unauthorized_error(request)

    if (request.method != 'GET'):
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    if not user:
        return Response({'message': 'user not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    scrolls_reported = user.reported_scrolls.all()
    scrolls_id_list = [{'id': scrolls.id} for scrolls in scrolls_reported]

    return Response({'reported_scrolls': scrolls_id_list}, status=status.HTTP_200_OK)

def get_remix_report_by_user(request):
    user = authenticate_then_user_or_unauthorized_error(request)

    if (request.method != 'GET'):
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    if not user:
        return Response({'message': 'user not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    remix_reported = user.reported_remix.all()
    remix_id_list = [remix.id for remix in remix_reported]

    return Response({'reported_remix': remix_id_list}, status=status.HTTP_200_OK)


