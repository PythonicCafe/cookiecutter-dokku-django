import hashlib
import logging
import pickle
import threading
import time
from typing import Any

from celery import Task
from django.conf import settings
from django.core.cache import caches

logger = logging.getLogger(__name__)


class LockedTask(Task):
    """A Celery Task subclass that prevents concurrent execution of tasks with identical arguments.

    This class uses Django's cache system to implement a distributed locking mechanism. Before
    a worker starts processing a task, it attempts to acquire a lock. If successful, the task
    executes; otherwise, it's skipped to prevent duplicate processing.

    Features:
    - Automatic lock refresh to prevent premature expiration during long-running tasks.
    - Configurable lock timeout and refresh intervals.
    - Graceful lock release after task completion or failure.

    Configuration (add to project's settings):
    - CELERY_TASK_LOCK_CACHE: Name of the Django cache to use (default: "default")
    - CELERY_TASK_LOCK_TIMEOUT: Lock expiration time in seconds (default: 180)
    - CELERY_TASK_LOCK_REFRESH: Lock refresh interval in seconds (default: 10)

    Usage as class-based task:
    ```python
    class MyTask(LockedTask):
        def run(self, *args, **kwargs):
            # Task logic here
            pass
    ```

    Usage as function-based task:
    ```python
    @shared_task(bind=True, base=LockedTask)
    def mytask(arg1, ...):
        # Task logic here
        pass
    ```

    Note:
    - Ensure that Django's cache backend is properly configured for distributed environments.
    - Skipped tasks (due to lock) are not automatically rescheduled. Implement custom logic if
      rescheduling is required for your use case.
    """

    abstract = True

    def __init__(self) -> None:
        super().__init__()
        self.cache = caches[getattr(settings, "CELERY_TASK_LOCK_CACHE", "default")]
        self.lock_expiration = getattr(settings, "CELERY_TASK_LOCK_TIMEOUT", 180)
        self.lock_refresh_interval = getattr(settings, "CELERY_TASK_LOCK_REFRESH", 10)
        self._lock_key: str = ""
        self._refresh_thread: threading.Thread | None = None

    @property
    def lock_key(self) -> str:
        """Generate a unique lock key based on the task name and arguments."""
        if not self._lock_key:
            args = self.request.args
            kwargs = sorted(self.request.kwargs.items())
            task_hash = hashlib.sha1(pickle.dumps((args, kwargs))).hexdigest()
            self._lock_key = f"LockedTask_{self.name}_{task_hash}"
        return self._lock_key

    def acquire_lock(self) -> bool:
        """Attempt to acquire the lock for this task."""
        result = self.cache.add(self.lock_key, True, self.lock_expiration)
        logger.info(
            "LockedTask: Acquiring lock key %r for task %s: %s",
            self.lock_key,
            self.request.id,
            "succeeded" if result else "failed",
        )
        return result

    def refresh_lock(self) -> None:
        """Periodically refresh the lock to prevent expiration during task execution."""
        while self.cache.get(self.lock_key):
            self.cache.set(self.lock_key, True, self.lock_expiration)
            time.sleep(self.lock_refresh_interval)

    def release_lock(self) -> None:
        """Release the lock and stop the refresh thread."""
        self.cache.delete(self.lock_key)
        if self._refresh_thread:
            self._refresh_thread.join()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the task if the lock can be acquired, otherwise skip it."""
        if self.acquire_lock():
            logger.info("LockedTask: Task %s execution with lock started", self.request.id)
            self._refresh_thread = threading.Thread(target=self.refresh_lock, daemon=True)
            self._refresh_thread.start()
            try:
                return super().__call__(*args, **kwargs)
            finally:
                self.release_lock()
        else:
            logger.warning("LockedTask: Task %s skipped (locked)", self.request.id)
