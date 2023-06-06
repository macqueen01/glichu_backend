"""mockingJae_back URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
import notifications.urls

from main.views import scrolls_browse, scrolls_of_user, \
    video_upload, scrollify_video_depricated, scrolls_upload, \
    task_status, random_scrolls, auto_recording_upload, auto_recording_from_scrolls, is_duplicate_user, \
    user_login, user_join, user_logout, user_login_with_token, \
    get_followings, get_followers, get_user, get_user_detail, self_profile, \
    reset_profile, reset_username, \
    follow_user, unfollow_user, is_user_self, has_tagged, tag_user, \
    get_scrolls_reported, get_remix_reported, report_remix, report_scrolls, \
    does_user_like_auto_recording, like_auto_recording, unlike_auto_recording \

urlpatterns = [
    path('browse/', random_scrolls),
    path('browse/user', scrolls_of_user),
    path('upload/video', video_upload),
    path('upload/scrollify', scrollify_video_depricated),
    path('upload/post', scrolls_upload),

    # auto recordings
    path('auto-recording/upload', auto_recording_upload),
    path('auto-recording/browse', auto_recording_from_scrolls),
    path('auto-recording/like', like_auto_recording),
    path('auto-recording/unlike', unlike_auto_recording),
    path('auto-recording/is-liked', does_user_like_auto_recording),

    # task query
    path('upload/task', task_status),

    # authentications
    path('auth/user-exists', is_duplicate_user),
    path('auth/login/token', user_login_with_token),
    path('auth/login', user_login),
    path('auth/join', user_join),
    path('auth/logout', user_logout),

    # user
    path('user/', get_user),
    path('user/detailed', get_user_detail),
    path('user/following', get_followings),
    path('user/follower', get_followers),
    path('user/self', self_profile),

    path('user/is-self', is_user_self),
    path('user/reset/username', reset_username),
    path('user/reset/profile', reset_profile),

    # social interactions
    path('user/follow', follow_user),
    path('user/unfollow', unfollow_user),

    # tag interactions
    path('tag/has-tagged', has_tagged),
    path('tag/', tag_user),


    # Reports

    path('report/scrolls', report_scrolls),
    path('report/remix', report_remix),
    path('report/browse/scrolls', get_scrolls_reported),
    path('report/browse/remix', get_remix_reported),

    # Notification

    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),

]
