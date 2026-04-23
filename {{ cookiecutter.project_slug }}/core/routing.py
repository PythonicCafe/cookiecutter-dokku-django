from django.urls import path

from core import consumers

websocket_urlpatterns = [
    path("ws/echo/", consumers.EchoConsumer.as_asgi()),
]
