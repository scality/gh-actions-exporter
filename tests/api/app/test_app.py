

def test_unsupported_events(client):
    """Ensure we don't crash on other workflow_run events"""
    headers = {"X-GitHub-Event": "push"}
    webhook = {
        "repository": {
            "name": "repo",
            "full_name": "org/repo",
            "visibility": "private",
        }
    }
    response = client.post("/webhook", json=webhook, headers=headers)

    assert response.status_code == 202


def test_ping(client):
    headers = {"X-GitHub-Event": "ping"}
    webhook = {"zen": "Anything added dilutes everything else."}
    response = client.post("/webhook", json=webhook, headers=headers)
    assert response.status_code == 202


def test_healthcheck(client):
    response = client.get("/")
    assert response.status_code == 200
