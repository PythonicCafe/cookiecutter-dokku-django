import json

import pytest
from channels.testing.websocket import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from core.consumers import EchoConsumer

User = get_user_model()


def _make_communicator(user=None):
    """Create a `WebsocketCommunicator` with an optional user in the scope."""
    communicator = WebsocketCommunicator(EchoConsumer.as_asgi(), "/ws/echo/")
    communicator.scope["user"] = user or AnonymousUser()
    return communicator


@pytest.mark.django_db(transaction=True)
async def test_echo_consumer_rejects_anonymous_user():
    communicator = _make_communicator()
    connected, _ = await communicator.connect()
    assert not connected
    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
async def test_echo_consumer_accepts_authenticated_user():
    user = await User.objects.acreate(username="ws-test", email="ws@test.com", is_active=True)
    communicator = _make_communicator(user=user)
    connected, _ = await communicator.connect()
    assert connected
    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
async def test_echo_consumer_echoes_message():
    user = await User.objects.acreate(username="ws-echo", email="echo@test.com", is_active=True)
    communicator = _make_communicator(user=user)
    await communicator.connect()
    await communicator.send_to(text_data="Hello WebSocket")
    response = await communicator.receive_from()
    data = json.loads(response)
    assert data == {"echo": "Hello WebSocket"}
    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
async def test_echo_consumer_ignores_bytes():
    user = await User.objects.acreate(username="ws-bytes", email="bytes@test.com", is_active=True)
    communicator = _make_communicator(user=user)
    await communicator.connect()
    await communicator.send_to(bytes_data=b"\x00\x01")
    assert await communicator.receive_nothing(timeout=0.5)
    await communicator.disconnect()
