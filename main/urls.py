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
from main.views import scrolls_browse, scrolls_of_user, \
    video_upload, scrollify_video, scrolls_upload, \
    task_status, random_scrolls, auto_recording_upload, auto_recording_from_scrolls, is_duplicate_user, \
    user_login, user_join, user_logout, user_login_with_token

urlpatterns = [
    path('browse/', random_scrolls),
    path('browse/user', scrolls_of_user),
    path('upload/video', video_upload),
    path('upload/scrollify', scrollify_video),
    path('upload/post', scrolls_upload),
    path('auto-recording/upload', auto_recording_upload),
    path('auto-recording/browse', auto_recording_from_scrolls),
    path('upload/task', task_status),
    path('auth/user-exists', is_duplicate_user),
    path('auth/login/token', user_login_with_token),
    path('auth/login', user_login),
    path('auth/join', user_join),
    path('auth/logout', user_logout),

]
