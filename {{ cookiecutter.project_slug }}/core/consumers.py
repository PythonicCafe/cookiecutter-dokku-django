import json
import logging

from channels.generic.websocket import WebsocketConsumer

logger = logging.getLogger(__name__)


class EchoConsumer(WebsocketConsumer):
    """Test consumer that echoes messages back to the client.

    Accepts only authenticated users. To test in the browser, open a page of the system, authenticate, and run in the
    console:

    ```javascript
    ws = new WebSocket((location.protocol === 'https:' ? 'wss' : 'ws') + '://' + location.host + '/ws/echo/');
    ws.onopen = () => { console.log('Connected'); ws.send('Hello'); };
    ws.onmessage = (e) => console.log('Response:', e.data);
    ws.onclose = (e) => console.log('Disconnected:', e.code);
    ```
    """

    def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            logger.info("ws/echo: connection refused (anonymous user)")
            self.close()
            return
        self.accept()
        logger.info(f"ws/echo: connection accepted (user_id={user.id})")

    def disconnect(self, close_code):
        user = self.scope.get("user")
        user_id = getattr(user, "id", None)
        logger.info(f"ws/echo: disconnected (user_id={user_id}, code={close_code})")

    def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
        self.send(text_data=json.dumps({"echo": text_data}))
