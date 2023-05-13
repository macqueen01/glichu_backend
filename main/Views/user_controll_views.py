from django.utils import timezone

from rest_framework.response import Response
from rest_framework import status, exceptions

from main.models import Scrolls, User, Recommendation
from main.serializer import *


def is_duplicate_user(request):
    try:
        if request.method != 'POST':
            return Response({'message': 'wrong method call'},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

        
        username = request.data['username']
        # get user with username 
        user = User.objects.filter(username=username)

        if (user.exists()):
            print('here')
            return Response({
                'message': f'user with id {username} is already occupied',
                'exists': 1
            }, status=status.HTTP_200_OK)
        return Response({
            'message': f'user with id {username} can be used',
            'exists': 0
        }, status=status.HTTP_200_OK)
    except:
        return Response({'message': 'argument missing'}, 
            status=status.HTTP_400_BAD_REQUEST)


from knox.models import AuthToken
from knox.settings import CONSTANTS
import requests

from rest_framework.response import Response
from rest_framework import status, exceptions

from main.Models.UserModel import User


def get_user_from_token(token):
    objs = AuthToken.objects.filter(token_key=token[:CONSTANTS.TOKEN_KEY_LENGTH])
    if len(objs) == 0:
        return None
    return objs.first().user

def logout_user(request):
    _, token = request.META.get('HTTP_AUTHORIZATION').split(' ')
    if request.method == 'POST':
        try:
            user = get_user_from_token(token)
            user.auth_token_set.all().delete()
            return Response({"message": "User logged out"},
                status = status.HTTP_200_OK)
        except:
            return Response({"message": "Token removal error"},
                status = status.HTTP_404_NOT_FOUND)

def login_user(request):
    if request.method == 'POST':
        try: 
            social_login_type = request.data['social_login_type']
            
            if social_login_type == 'instagram':

                access_token = request.data['access_token']
                response = requests.get(f'https://graph.instagram.com/me?fields=id,username&access_token={access_token}')
                data = response.json()

                if 'error' in data:
                    # Handle error response from Instagram API
                    return Response({'error': 'Invalid access token'}, status = status.HTTP_400_BAD_REQUEST)
                

                if not User.objects.filter(instagram_id=data['id']).exists():
                    message = {'message': "no user found with this instagram_id"}
                    return Response(message, status = status.HTTP_404_NOT_FOUND)
                
                user = User.objects.get(instagram_id=data['id'])

            elif social_login_type == 'apple':
                # TODO: need to implement social login case for apple
                pass
            
            else:
                return Response({'message': "wrong social login type"}, status = status.HTTP_400_BAD_REQUEST)


            return Response(
                {
                    "user": user.username,
                    "social_login_type": social_login_type,
                    "instagram_id": user.instagram_id,
                    "apple_id": user.apple_id,
                    "token": AuthToken.objects.create(user)[1]
                }
            )
        
        except:
            return Response({'message': "argument missing"}, status = status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': "wrong method call"}, status = status.HTTP_405_METHOD_NOT_ALLOWED)


def create_user(request):
    if request.method == 'POST':
        try: 
            username = request.data['username']
            social_login_type = request.data['social_login_type']
            client_ip = request.META.get("REMOTE_ADDR")
            
            if User.objects.filter(username=request.data['username']).exists():
                message = {'message': "duplicate user"}
                return Response(message, status = status.HTTP_400_BAD_REQUEST) 

            if social_login_type == 'instagram':
                access_token = request.data['access_token']
                response = requests.get(f'https://graph.instagram.com/me?fields=id,username&access_token={access_token}')
                data = response.json()

                if 'error' in data:
                    # Handle error response from Instagram API
                    return Response({'error': 'Invalid access token'}, status = status.HTTP_400_BAD_REQUEST)
                
                instagram_id = data['id']

                # check if user with same instagram_id exists
                if (User.objects.filter(instagram_id=instagram_id).exists()):
                    return Response({'message': "duplicate user"}, status = status.HTTP_400_BAD_REQUEST)

                user = User.objects.create_user_with_instagram_id(username, instagram_id)

            elif social_login_type == 'apple':
                # TODO: need to implement social login case for apple
                pass
            
            else:
                return Response({'message': "wrong social login type"}, status = status.HTTP_400_BAD_REQUEST)


            user.client_ip = client_ip
            user.save()


            return Response(
                {
                    "user": username,
                    "social_login_type": social_login_type,
                    "instagram_id": user.instagram_id,
                    "apple_id": user.apple_id,
                    "token": AuthToken.objects.create(user)[1]
                }
            )
        
        except:
            return Response({'message': "argument missing"}, status = status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': "wrong method call"}, status = status.HTTP_405_METHOD_NOT_ALLOWED)

def check_duplicate_devices(request):
    pass



            