from django.urls import path
from main.Websocket.Consumers import post_scrolls

websocket_urlpatterns = [
    path('ws/scrolls-upload/', post_scrolls.ScrollsUploadConsumer.as_asgi()),
]