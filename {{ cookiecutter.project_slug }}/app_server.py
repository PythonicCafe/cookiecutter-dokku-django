import os
import signal
import threading
import time

from uvicorn_worker import UvicornWorker


class _AliveWatcher(threading.Thread):
    """Workaround for gunicorn's reloader not restarting UvicornWorker correctly.

    Gunicorn's reloader sets `worker.alive = False` and calls `sys.exit(0)`, which in `UvicornWorker` only kills the
    reloader thread (not the asyncio process). This watcher signals the process when `alive` flips to False so the
    arbiter actually respawns it.

    References:
    - <https://github.com/benoitc/gunicorn/issues/2339>
    - <https://github.com/Kludex/uvicorn/discussions/1638>
    """

    def __init__(self, worker, interval: float = 1.0):
        super().__init__(daemon=True)
        self._worker = worker
        self._interval = interval

    def run(self):
        while True:
            if not self._worker.alive:
                os.kill(os.getpid(), signal.SIGTERM)
                return
            time.sleep(self._interval)


class HeartbeatUvicornWorker(UvicornWorker):
    """Uvicorn worker with active WebSocket protocol ping/pong.

    Dokku's nginx has `proxy-read-timeout=60s` by default. Pings every 25s keep the connection alive with a
    comfortable margin. A 10s timeout closes the connection if the client does not reply to the pong.
    """

    CONFIG_KWARGS = {
        "loop": "auto",
        "http": "auto",
        "ws": "auto",
        "ws_ping_interval": 25.0,
        "ws_ping_timeout": 10.0,
    }

    def init_process(self):
        if self.cfg.reload:
            _AliveWatcher(self).start()
        super().init_process()
