import time
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


from django.utils import timezone
import requests

from knox.models import AuthToken
from knox.settings import CONSTANTS

from rest_framework.response import Response
from rest_framework import status, exceptions
from main.Views.authentications import authenticate_then_user_or_unauthorized_error, get_user_from_token

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

def is_user_self(request, target_id):

    user = authenticate_then_user_or_unauthorized_error(request)

    if user is None:
        return Response({'message': 'user is invalid'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method != 'GET':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    if user.id == target_id:
        return Response({'message': 'user is self', 'is_self': 1}, status=status.HTTP_200_OK)
    
    return Response({'message': 'user is not self', 'is_self': 0}, status=status.HTTP_200_OK)

def user_fetch(request):

    user = authenticate_then_user_or_unauthorized_error(request)

    if user is None:
        return Response({'message': 'user is invalid'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method != 'GET':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    serialized_user = UserSerializerForSelfProfile
    result = serialized_user(user)
    return Response(result.data, status=status.HTTP_200_OK)

def user_fetch(request):

    user = authenticate_then_user_or_unauthorized_error(request)

    if user is None:
        return Response({'message': 'user is invalid'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method != 'GET':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    serialized_user = UserSerializerForSelfProfile
    result = serialized_user(user)
    return Response(result.data, status=status.HTTP_200_OK)


def reset_profile_image(request):

    user = authenticate_then_user_or_unauthorized_error(request)

    if user is None:
        return Response({'message': 'user is invalid'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'POST':

        try:
            profile_image = request['profile_image']
            user.profile_image = profile_image
            user.save()
            return Response({'message': 'profile image is updated'}, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'profile image is missing'}, status=status.HTTP_404_NOT_FOUND)
        
    return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            


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
        
def login_user_with_token(request):
    if request.method == 'POST':
        try:
            token = request.data['token']
            user = get_user_from_token(token)
            if user is None:
                return Response({"message": "Token is invalid"},
                    status = status.HTTP_404_NOT_FOUND)
            else:
                user = UserSerializerForScrolls(user)
                return Response(user.data,
                    status = status.HTTP_200_OK)
        except:
            return Response({"message": "Token is invalid"},
                status = status.HTTP_404_NOT_FOUND)
    return Response({'message': "wrong method call"}, status = status.HTTP_405_METHOD_NOT_ALLOWED)



def _apple_social_authenticate_then_return_user_id(request):
    # Retrieve data from the request
    authentication_code = request.data['authorization_code']
    user_identifier = request.data['user_identifier']
    identity_token = request.data['access_token']

    # Generate the client_secret
    client_id = os.environ.get('CLIENT_ID')
    team_id = os.environ.get('TEAM_ID')
    key_id = os.environ.get('KEY_ID')
    private_key = settings.APPLE_PRIVATE_KEY


    headers = {
        'kid': key_id,
        'alg': 'ES256',
    }

    payload = {
        'iss': team_id,
        'iat': int(time.time()),
        'exp': int(time.time() + 8640),  # Expiration time in seconds (180 days in this example)
        'aud': 'https://appleid.apple.com',
        'sub': client_id,
    }

    client_secret = jwt.encode(payload=payload, key=private_key, algorithm='ES256', headers=headers)

    # Send a request to Apple's token endpoint to exchange the authentication code for tokens
    apple_token_url = 'https://appleid.apple.com/auth/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': authentication_code,
        'grant_type': 'authorization_code',
    }
    response = requests.post(apple_token_url, data=data)

    if response.status_code != status.HTTP_200_OK:
        return Response({'error': 'Failed to authenticate with Apple'}, status=status.HTTP_401_UNAUTHORIZED)

    # Extract the access token and verify the identity token
    fetched_id_token = response.json().get('id_token')
    fetched_user_identifier = jwt.decode(fetched_id_token, options={'verify_signature': False}).get('sub')

    # Check if the user identifier matches the Apple user ID
    if user_identifier != fetched_user_identifier:
        return False


    return user_identifier

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
                user_id = _apple_social_authenticate_then_return_user_id(request)

                if not user_id:
                    return Response({'message': 'invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
                
                if not User.objects.filter(apple_id = user_id).exists():
                    return Response({'message': 'user is not registered'}, status=status.HTTP_404_NOT_FOUND)
                
                user = User.objects.get(apple_id=user_id)
            
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
            profile_image = request.data['profile_image']

            
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
                instagram_username = data['username']

                # check if user with same instagram_id exists
                if (User.objects.filter(instagram_id=instagram_id).exists()):
                    return Response({'message': "duplicate user"}, status = status.HTTP_400_BAD_REQUEST)

                user = User.objects.create_user_with_instagram_id(username, instagram_id, instagram_username)

            elif social_login_type == 'apple':
                # TODO: need to implement social login case for apple
                user_id = _apple_social_authenticate_then_return_user_id(request)

                if not user_id:
                    return Response({'message': 'invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
                
                if User.objects.filter(apple_id = user_id).exists():
                    return Response({'message': 'duplicate user'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                
                user = User.objects.create_user_with_apple_id(username, user_id)
                print(user.apple_id)
            
            else:
                return Response({'message': "wrong social login type"}, status = status.HTTP_400_BAD_REQUEST)

            if (profile_image != None):
                user.profile_image = profile_image

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

