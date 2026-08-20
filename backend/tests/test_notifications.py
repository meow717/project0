"""End-to-end tests for the notifications feature (use cases + HTTP API)."""

import pytest

from src.notifications.application.use_cases import SendNotificationCommand
from src.notifications.container import container


@pytest.fixture
def user_with_token(client):
    reg = client.post(
        "/api/auth/register",
        data={"email": "n@x.com", "password": "password123", "full_name": "N"},
        content_type="application/json",
    )
    assert reg.status_code == 201
    login = client.post(
        "/api/auth/login",
        data={"email": "n@x.com", "password": "password123"},
        content_type="application/json",
    )
    return {
        "client": client,
        "headers": {"Authorization": f"Bearer {login.json()['tokens']['access_token']}"},
    }


@pytest.mark.django_db
def test_send_and_list(user_with_token):
    client = user_with_token["client"]
    headers = user_with_token["headers"]

    # Send one notification directly (simulates queue alert).
    from src.accounts.models import UserModel

    user = UserModel.objects.get(email="n@x.com")
    c = container()
    c.send_notification.execute(
        SendNotificationCommand(
            user_id=user.id,
            title="Your turn is coming",
            body="Ticket A-001 is almost up",
            kind="in_app",
            ref_kind="queue",
            ref_id=1,
        )
    )

    listed = client.get("/api/notifications/mine", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["title"] == "Your turn is coming"

    unread = client.get("/api/notifications/unread", headers=headers)
    assert unread.json()["unread_count"] == 1

    marked = client.patch(f"/api/notifications/{listed.json()[0]['id']}/read", headers=headers)
    assert marked.status_code == 204

    unread2 = client.get("/api/notifications/unread", headers=headers)
    assert unread2.json()["unread_count"] == 0


@pytest.mark.django_db
def test_cannot_mark_others_notification(user_with_token):
    client = user_with_token["client"]
    headers = user_with_token["headers"]

    # second user
    client.post(
        "/api/auth/register",
        data={"email": "n2@x.com", "password": "password123", "full_name": "N2"},
        content_type="application/json",
    )
    login2 = client.post(
        "/api/auth/login",
        data={"email": "n2@x.com", "password": "password123"},
        content_type="application/json",
    )
    headers2 = {"Authorization": f"Bearer {login2.json()['tokens']['access_token']}"}

    from src.accounts.models import UserModel

    user = UserModel.objects.get(email="n@x.com")
    c = container()
    c.send_notification.execute(
        SendNotificationCommand(user_id=user.id, title="T", body="B", kind="in_app")
    )

    listed = client.get("/api/notifications/mine", headers=headers)
    other = client.patch(f"/api/notifications/{listed.json()[0]['id']}/read", headers=headers2)
    assert other.status_code == 404
