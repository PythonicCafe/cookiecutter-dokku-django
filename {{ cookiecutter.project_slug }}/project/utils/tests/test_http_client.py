import responses

from project.utils.http_client import BaseClient, create_session


def test_create_session():
    session = create_session()
    assert "User-Agent" not in session.headers
    assert "application/json" in session.headers["Accept"]

    user_agent = "My User Agent 1.0"
    session = create_session(user_agent=user_agent)
    assert "User-Agent" in session.headers
    assert session.headers["User-Agent"] == user_agent


@responses.activate
def test_base_client_request_success():
    responses.add(responses.GET, "https://api.example.com/test", json={"ok": True}, status=200)
    client = BaseClient()
    resp = client.request("GET", "https://api.example.com/test")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


@responses.activate
def test_base_client_retries_on_500():
    responses.add(responses.GET, "https://api.example.com/retry", status=500)
    responses.add(responses.GET, "https://api.example.com/retry", json={"ok": True}, status=200)
    client = BaseClient(wait_time=0.001)
    resp = client.request("GET", "https://api.example.com/retry", max_tries=2)
    assert resp.status_code == 200
