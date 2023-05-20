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
            username = request.data['username']
            social_login_type = request.data['social_login_type']
            
            if not User.objects.filter(username=request.data['username']).exists():
                message = {'message': "no user found with this username"}
                return Response(message, status = status.HTTP_404_NOT_FOUND)

            if social_login_type == 'instagram':
                access_token = request.data['access_token']
                response = requests.get(f'https://graph.instagram.com/me?fields=id,username&access_token={access_token}')
                data = response.json()

                if 'error' in data:
                    # Handle error response from Instagram API
                    return Response({'error': 'Invalid access token'}, status = status.HTTP_400_BAD_REQUEST)
                
                user = User.objects.create_user_with_instagram_id(username)

            elif social_login_type == 'apple':
                # TODO: need to implement social login case for apple
                pass
            
            else:
                return Response({'message': "wrong social login type"}, status = status.HTTP_400_BAD_REQUEST)


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
                user_id = request.data['user_id']
                response = requests.get(f'https://graph.instagram.com/me?fields=id,username&access_token={access_token}')
                data = response.json()

                if 'error' in data:
                    # Handle error response from Instagram API
                    return Response({'error': 'Invalid access token'}, status = status.HTTP_400_BAD_REQUEST)
                
                if data['id'] != user_id:
                    # if user_id from request and user_id from instagram api is different
                    return Response({'error': 'Invalid user id'}, status = status.HTTP_400_BAD_REQUEST)
                
                user = User.objects.create_user_with_instagram_id(username)

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