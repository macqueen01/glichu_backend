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



def does_user_like_auto_recording(request, remix_id):

    user = authenticate_then_user_or_unauthorized_error(request)

    if request.method != 'GET':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    if not user:
        return Response({'message': 'user not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    remix = Remix.objects.get(id=remix_id)

    if not remix:
        return Response({'message': 'remix not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    is_liked = Remix.objects.does_user_like_remix(user.id, remix.id)

    if is_liked:
        is_liked = 1
    else:
        is_liked = 0

    return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)


def like_auto_recording(request, remix_id):
    user = authenticate_then_user_or_unauthorized_error(request)

    if request.method != 'POST':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    if not user:
        return Response({'message': 'user not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    remix = Remix.objects.get(id=remix_id)

    if not remix:
        return Response({'message': 'remix not found'},
            status=status.HTTP_404_NOT_FOUND)
    

    Remix.objects.like_remix(user.id, remix.id)

    return Response({'message': 'success'}, status=status.HTTP_200_OK)



def unlike_auto_recording(request, remix_id):
    user = authenticate_then_user_or_unauthorized_error(request)

    if request.method != 'POST':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    if not user:
        return Response({'message': 'user not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    remix = Remix.objects.get(id=remix_id)

    if not remix:
        return Response({'message': 'remix not found'},
            status=status.HTTP_404_NOT_FOUND)
    

    Remix.objects.unlike_remix(user.id, remix.id)

    return Response({'message': 'success'}, status=status.HTTP_200_OK)



def get_saved_auto_recording(request, user_id):
    user = authenticate_then_user_or_unauthorized_error(request)

    if request.method != 'GET':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    if not user:
        return Response({'message': 'user not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    target = User.objects.get(id=user_id)

    if not target:
        return Response({'message': 'target not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    saved_remixes = Remix.objects.filter(saved_by_scrolls_uploader=1, scrolls__created_by=target).order_by('-created_at')

    serialized_remixes = RemixViewSerializerWithRawJson(saved_remixes, many=True, context={'user': user}).data
    return Response({'remixes': serialized_remixes}, status=status.HTTP_200_OK)


def save_auto_recording(request):

    user = authenticate_then_user_or_unauthorized_error(request)

    remix_id = request.data['remix_id']

    if request.method != 'POST':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    if not user:
        return Response({'message': 'user not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    remix = Remix.objects.get(id=remix_id)

    if not remix:
        return Response({'message': 'remix not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    if remix.scrolls.created_by.id != user.id:
        return Response({'message': 'user not authorized'},
            status=status.HTTP_401_UNAUTHORIZED)
    
    if remix.saved_by_scrolls_uploader == 1:
        return Response({'message': 'already saved'},
            status=status.HTTP_400_BAD_REQUEST)
    
    remix.saved_by_scrolls_uploader = 1
    remix.save()

    return Response({'message': 'success'}, status=status.HTTP_200_OK)


def unsave_auto_recording(request, remix_id):
    
    user = authenticate_then_user_or_unauthorized_error(request)

    remix_id = request.data['remix_id']
    
    if request.method != 'POST':
        return Response({'message': 'wrong method call'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
       
    if not user:
        return Response({'message': 'user not found'},
            status=status.HTTP_404_NOT_FOUND)
    
    remix = Remix.objects.get(id=remix_id)

    if not remix:
        return Response({'message': 'remix not found'},
            status=status.HTTP_404_NOT_FOUND)
        
    if remix.scrolls.created_by.id != user.id:
        return Response({'message': 'user not authorized'},
            status=status.HTTP_401_UNAUTHORIZED)
        
    if remix.saved_by_scrolls_uploader == 0:
        return Response({'message': 'already unsaved'},
            status=status.HTTP_400_BAD_REQUEST)
        
    remix.saved_by_scrolls_uploader = 0
    remix.save()
    
    return Response({'message': 'success'}, status=status.HTTP_200_OK)
    




def get_auto_recording_from_scrolls(request, 
                                    scrolls_id, 
                                    by_recent = True, 
                                    by_most_scrolled = False, 
                                    by_followers=False,
                                    mp4 = True
                                    ):
    user = authenticate_then_user_or_unauthorized_error(request)

    if (request.method == 'GET'):

        # assert(request.data['scrolls_id'])
        scrolls = Scrolls.objects.get(id=int(scrolls_id))

        if not scrolls:
            return Response({'message': 'scrolls not found'},
                status=status.HTTP_404_NOT_FOUND)
        
        if mp4:
            browse_cases = Remix.objects.filter(uploaded_to_s3__exact = 1).filter(scrolls__pk = scrolls.id)
            serializer = RemixViewSerializer
        else:
            browse_cases = Remix.objects.filter(scrolls__pk = scrolls.id)
            serializer = RemixViewSerializerWithRawJson

        


        if by_most_scrolled:
            browse_cases = browse_cases.order_by('task_queue_json')
        
        if by_recent:
            browse_cases = browse_cases.order_by('-created_at')

        if by_followers:
            browse_cases = browse_cases.filter(user__in = user.followers.all()).order_by('-created_at')


        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(browse_cases, request)
        serializer = serializer(result_page, many=True, context={'user': user})
        return paginator.get_paginated_response(serializer.data)
    
    return Response({'message': "wrong method call"}, 
        status = status.HTTP_405_METHOD_NOT_ALLOWED)


def upload_auto_recording_as_mp4(request):
    return _upload_auto_recording(request)

def upload_auto_recording_as_raw_text(request):
    try:
        if request.method == 'POST':
            
            assert(request.data['timeline'] and 
                   request.data['title'] and 
                   request.data['length'] and
                   request.data['scrolls'] and
                   request.data['token'])
            
            user = get_user_from_token(request.data['token'])
            scrolls = Scrolls.objects.get(id=int(request.data['scrolls'].split('_')[0]))

            if not user:
                return Response({'message': 'invalid token'},
                    status=status.HTTP_401_UNAUTHORIZED)
            
            parsed_request = {
                'timeline': request.data['timeline'],
                'title': request.data['title'],
                'length': request.data['length'],
                'scrolls': request.data['scrolls'],
                'user': user.id
            }

            new_remix = Remix.objects.create_remix(
                title=request.data['title'],
                scrolls=scrolls,
                remix_directory='/',
                user=user,
            )

            new_remix.task_queue_json = json.dumps(parsed_request)
            Scrolls.objects.increase_scrolled(scrolls.id)
            new_remix.save()

            try:
                notify.send(sender=user, recipient=scrolls.created_by, verb='has scrolled your post', action_object=new_remix)
            except Exception as e:
                print(e)

                
            return Response({'message': 'remix upload as raw json successfull'},
                status=status.HTTP_200_OK)

    except:
        return Response({'message': 'argument missing'}, 
            status=status.HTTP_400_BAD_REQUEST)


def _upload_auto_recording(request):
    try:
        if request.method == 'POST':
            
            assert(request.data['timeline'] and 
                   request.data['title'] and 
                   request.data['length'] and
                   request.data['scrolls'] and
                   request.data['token'])
            
            user = get_user_from_token(request.data['token'])
            scrolls = Scrolls.objects.get(id=int(request.data['scrolls'].split('_')[0]))

            if not user:
                return Response({'message': 'invalid token'},
                    status=status.HTTP_401_UNAUTHORIZED)
            
            parsed_request = {
                'timeline': request.data['timeline'],
                'title': request.data['title'],
                'length': request.data['length'],
                'scrolls': request.data['scrolls'],
                'user': user.id
            }

            new_remix = Remix.objects.create_remix(
                title=request.data['title'],
                scrolls=scrolls,
                remix_directory='/',
                user=user,
            )

            new_remix.task_queue_json = json.dumps(parsed_request)
            Scrolls.objects.increase_scrolled(scrolls.id)
            
            new_remix.save()

            if task := tasks.remix_to_video.delay(remix_id=new_remix.id):
                return Response({
                    'message': 'task launched successful',
                    'task_id': f'{task.id}'
                    }, status = status.HTTP_200_OK)
                
            return Response({'message': 'task launch unsuccessful'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except:
        return Response({'message': 'argument missing'}, 
            status=status.HTTP_400_BAD_REQUEST)


