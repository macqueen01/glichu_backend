from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

from main.Views import browse_scrolls, post_scrolls, \
    auto_recording, user_controll_views, social_activities

@api_view(['GET'])
def scrolls_browse(request):
    scrolls_id = int(request.query_params['id'])
    return browse_scrolls.scrolls_with_given_id(request, scrolls_id)

@api_view(['GET'])
#@permission_classes([IsAuthenticated,])
def scrolls_of_user(request):
    user_id = int(request.query_params['id'])
    return browse_scrolls.get_scrolls_by_user(request, user_id)

@api_view(['GET'])
def random_scrolls(request):
    return browse_scrolls.get_random_scrolls(request)

@api_view(['GET'])
def auto_recording_from_scrolls(request):
    scrolls_id = int(request.query_params['id'])
    by_recent, by_most_scrolled, by_followers = False, False, False
    if (request.query_params.keys().__contains__('recent')):
        by_recent = True
    elif (request.query_params.keys().__contains__('most-scrolled')):
        by_most_scrolled = True
    elif (request.query_params.keys().__contains__('followers')):
        by_followers = True

    return auto_recording.get_auto_recording_from_scrolls(request, scrolls_id, by_recent, by_most_scrolled, by_followers)

@api_view(['POST'])
def video_upload(request):
    return post_scrolls.upload_video(request)

@api_view(['POST'])
def scrollify_video(request):
    return post_scrolls.scrollify_video(request)

@api_view(['POST'])
def scrolls_upload(request):
    return post_scrolls.upload_scrolls(request)

@api_view(['POST'])
def auto_recording_upload(request):
    return auto_recording.upload_auto_recording(request)

@api_view(['POST'])
def task_status(request):
    return post_scrolls.task_status(request)


# User controll views

@api_view(['POST'])
def is_duplicate_user(request):
    return user_controll_views.is_duplicate_user(request)

@api_view(['POST'])
def user_login_with_token(request):
    return user_controll_views.login_user_with_token(request)

@api_view(['POST'])
def user_login(request):
    return user_controll_views.login_user(request)

@api_view(['POST'])
def user_join(request):
    return user_controll_views.create_user(request)

@api_view(['POST'])
def user_logout(request):
    return user_controll_views.logout_user(request)


# Social Interactions

@api_view(['GET'])
def get_followers(request):
    user_id = int(request.query_params['id'])
    return social_activities.get_followers(request, user_id)

@api_view(['GET'])
def get_followings(request):
    user_id = int(request.query_params['id'])
    return social_activities.get_followings(request, user_id)

@api_view(['GET'])
def get_user(request):
    user_id = int(request.query_params['id'])
    return social_activities.get_user(request, user_id)
    

