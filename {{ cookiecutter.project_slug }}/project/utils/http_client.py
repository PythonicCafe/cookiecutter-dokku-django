import time

import requests
import urllib3
from requests.adapters import HTTPAdapter, Retry

urllib3.disable_warnings()


def create_session(user_agent=None) -> requests.Session:
    """Create a requests Session configured with retry policy and default headers."""
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(total=7, backoff_factor=1, respect_retry_after_header=False))
    if user_agent is not None:
        session.headers["User-Agent"] = user_agent
    session.headers["Accept"] = (
        "application/json,text/html,application/xhtml+xml,application/xml,application/pdf,text/csv,application/zip,application/x-zip-compressed"
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class BaseClient:
    """Base HTTP client with exponential backoff retries and proxy support."""

    def __init__(
        self,
        timeout: int = 30,
        wait_time: float = 1.0,
        wait_factor: float = 2.0,
        max_tries: int = 10,
        proxies: dict[str, str] | None = None,
        user_agent: str = "Mozilla/5.0 (compatible; Python Scraper)",
    ):
        self.session = create_session(user_agent=user_agent)
        if proxies is not None:
            self.session.proxies.update(proxies)
        self.proxies = proxies
        self.timeout = timeout
        self.wait_time = wait_time
        self.max_tries = max_tries
        self.wait_factor = wait_factor

    def request(self, *args, **kwargs) -> requests.Response:
        max_tries = kwargs.pop("max_tries", self.max_tries)
        kwargs["proxies"] = kwargs.get("proxies", self.proxies)
        tries = 0
        wait_time = self.wait_time
        while tries < max_tries:
            response = self.session.request(*args, **kwargs)
            if response.status_code < 500 and response.status_code != 429:
                return response
            tries += 1
            if tries == max_tries:
                response.raise_for_status()
            if self.wait_time is not None:
                time.sleep(wait_time)
                wait_time *= self.wait_factor
