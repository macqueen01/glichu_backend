from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from main.consumers import NotificationConsumer

websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]