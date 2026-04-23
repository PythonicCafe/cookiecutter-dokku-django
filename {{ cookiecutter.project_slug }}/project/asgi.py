"""
ASGI config for the project.

{% if cookiecutter.enable_channels == "y" -%}
Routes HTTP to the standard Django app and WebSocket to Channels (with session/cookie authentication and origin
validation via `ALLOWED_HOSTS`).
{%- else -%}
It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
{%- endif %}
"""

import os

{% if cookiecutter.enable_channels == "y" -%}
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
{% endif -%}
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

{% if cookiecutter.enable_channels == "y" -%}
django_asgi_app = get_asgi_application()

from core.routing import websocket_urlpatterns  # noqa: E402 (needs Django to be initialized first)


ws_app = AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)))
application = ProtocolTypeRouter({"http": django_asgi_app, "websocket": ws_app})
{%- else -%}
application = get_asgi_application()
{%- endif %}
