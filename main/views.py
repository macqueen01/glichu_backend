from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

from main.Views import browse_scrolls, post_scrolls, \
    auto_recording, user_controll_views, social_activities, tag_interactions, sounds, reports

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
def get_personalized_scrolls(request):
    return browse_scrolls.get_personalized_scrolls_feed(request)

@api_view(['POST'])
def save_scrolls(request):
    scrolls_id = int(request.query_params['id'])
    return social_activities.save_scrolls(request, scrolls_id)

@api_view(['POST'])
def unsave_scrolls(request):
    scrolls_id = int(request.query_params['id'])
    return social_activities.unsave_scrolls(request, scrolls_id)

@api_view(['GET'])
def saved_scrolls_of_user(request):
    user_id = int(request.query_params['id'])
    return browse_scrolls.get_saved_scrolls_of_user(request, user_id)

@api_view(['POST'])
def delete_scrolls(request):
    scrolls_id = int(request.query_params['id'])
    return post_scrolls.delete_scrolls(request, scrolls_id)

@api_view(['GET'])
def does_user_like_auto_recording(request):
    auto_recording_id = int(request.query_params['id'])
    return auto_recording.does_user_like_auto_recording(request, auto_recording_id)

@api_view(['POST'])
def like_auto_recording(request):
    auto_recording_id = int(request.query_params['id'])
    return auto_recording.like_auto_recording(request, auto_recording_id)

@api_view(['POST'])
def unlike_auto_recording(request):
    auto_recording_id = int(request.query_params['id'])
    return auto_recording.unlike_auto_recording(request, auto_recording_id)


@api_view(['POST'])
def auto_recording_save(request):
    return auto_recording.save_auto_recording(request)

@api_view(['POST'])
def auto_recording_unsave(request):
    return auto_recording.unsave_auto_recording(request)


@api_view(['GET'])
def auto_recording_from_scrolls(request):
    scrolls_id = int(request.query_params['id'])
    is_mp4 = request.query_params['mp4']

    if is_mp4 == 'true' or is_mp4 == 'True':
        is_mp4 = True
    else:
        is_mp4 = False

    by_recent, by_most_scrolled, by_followers = False, False, False
    if (request.query_params.keys().__contains__('recent')):
        by_recent = True
    elif (request.query_params.keys().__contains__('most-scrolled')):
        by_most_scrolled = True
    elif (request.query_params.keys().__contains__('followers')):
        by_followers = True


    return auto_recording.get_auto_recording_from_scrolls(request, scrolls_id, by_recent, by_most_scrolled, by_followers, mp4=is_mp4)


@api_view(['GET'])
def saved_auto_recording(request):
    user_id = int(request.query_params['id'])
    return auto_recording.get_saved_auto_recording(request, user_id)

@api_view(['POST'])
def video_upload(request):
    return post_scrolls.upload_video(request)

@api_view(['POST'])
def scrolls_upload(request):
    return post_scrolls.scrolls_upload_without_scrollify(request)


@api_view(['POST'])
def auto_recording_upload(request):
    return auto_recording.upload_auto_recording_as_raw_text(request)

@api_view(['POST'])
def auto_recording_mp4(request):
    return auto_recording.upload_auto_recording_as_mp4(request)

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

@api_view(['POST'])
def user_delete(request):
    return user_controll_views.delete_user(request)

@api_view(['GET'])
def self_profile(request):
    return user_controll_views.user_fetch(request)

@api_view(['POST'])
def reset_username(request):
    return user_controll_views.reset_username(request)

@api_view(['POST'])
def reset_profile(request):
    return user_controll_views.reset_profile_image(request)


# User Controll - Utilities

@api_view(['GET'])
def is_user_self(request):
    target_id = int(request.query_params['id'])
    return user_controll_views.is_user_self(request, target_id)


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

@api_view(['GET'])
def get_user_detail(request):
    user_id = int(request.query_params['id'])
    return social_activities.get_user_detail(request, user_id)

@api_view(['POST'])
def follow_user(request):
    user_id = int(request.query_params['id'])
    return social_activities.follow(request, user_id)

@api_view(['POST'])
def unfollow_user(request):
    user_id = int(request.query_params['id'])
    return social_activities.unfollow(request, user_id)



# Tagging interactions

@api_view(['GET'])
def has_tagged(request):
    target_id = int(request.query_params['id'])
    return tag_interactions.has_tagged(request, target_id)

@api_view(['POST'])
def tag_user(request):
    inviter_id = int(request.query_params['id'])
    return tag_interactions.accept_invitation(request, inviter_id)

# Sound interactions

@api_view(['GET'])
def get_freesound_sounds(request):
    if not (request.query_params.keys().__contains__('page')):
        page = 1
    else:
        page = int(request.query_params['page'])
    return sounds.get_freesound_sounds(request, page)


# Reports

@api_view(['GET'])
def get_scrolls_reported(request):
    return reports.get_scrolls_report_by_user(request)

@api_view(['GET'])
def get_remix_reported(request):
    return reports.get_remix_report_by_user(request)

@api_view(['POST'])
def report_scrolls(request):
    scrolls_id = int(request.query_params['id'])
    return reports.raise_scrolls_report(request, scrolls_id)

@api_view(['POST'])
def report_remix(request):
    remix_id = int(request.query_params['id'])
    return reports.raise_remix_report(request, remix_id)

@api_view(['POST'])
def report_user(request):
    user_id = int(request.query_params['id'])
    return reports.raise_user_report(request, user_id)

# Sounds
@api_view(['GET'])
def get_sounds(request):
    try:
        page = int(request.query_params['page'])
    except:
        page = 1

    try:
        query = request.query_params['query']
    except:
        query = ''
        
    return sounds.get_freesound_sounds(request, page, query)


# DEPRICATED APIS

@api_view(['POST'])
def scrollify_video_depricated(request):
    return post_scrolls.scrollify_video(request)

@api_view(['POST'])
def scrolls_upload_depricated(request):
    return post_scrolls.upload_scrolls(request)
