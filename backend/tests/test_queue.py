"""Tests for the queue feature (wait estimator, use cases, HTTP API)."""

import pytest

from src.queue.domain.entities import (
    STATUS_CALLED,
    STATUS_IN_PROGRESS,
    STATUS_SERVED,
    STATUS_WAITING,
    QueueEntry,
    Service,
)
from src.queue.domain.wait_estimator import estimate_wait, position_of, update_avg_duration


# --------------------------------------------------------------------------- #
# Pure domain: wait estimator
# --------------------------------------------------------------------------- #
def test_update_avg_duration_ema():
    # 600 * 0.2 + 900 * 0.8 = 840
    assert update_avg_duration(900, 600) == 840
    assert update_avg_duration(840, 0) == 840  # invalid durations ignored


def test_estimate_wait_sums_ahead():
    from datetime import UTC, datetime, timedelta

    now = datetime.now(UTC)
    svc = Service(id=1, business_id=1, name="A", ticket_prefix="A", avg_duration_sec=600)
    services = {1: svc}
    # One in progress (elapsed 120s -> remaining 480), two waiting -> 1200
    in_progress = QueueEntry(
        id=1, business_id=1, service_id=1, ticket_number=1, ticket_code="A-001",
        status=STATUS_IN_PROGRESS, started_at=now - timedelta(seconds=120),
    )
    w1 = QueueEntry(
        id=2, business_id=1, service_id=1, ticket_number=2,
        ticket_code="A-002", status=STATUS_WAITING,
    )
    w2 = QueueEntry(
        id=3, business_id=1, service_id=1, ticket_number=3,
        ticket_code="A-003", status=STATUS_WAITING,
    )
    entries = [in_progress, w1, w2]
    assert estimate_wait(entries, services, now) == 480 + 600 + 600


def test_position_of():
    a = QueueEntry(
        id=1, business_id=1, service_id=1, ticket_number=1,
        ticket_code="A-001", status=STATUS_WAITING,
    )
    b = QueueEntry(
        id=2, business_id=1, service_id=1, ticket_number=2,
        ticket_code="A-002", status=STATUS_WAITING,
    )
    assert position_of(b, [a, b]) == 2
    assert position_of(a, [a, b]) == 1


# --------------------------------------------------------------------------- #
# Full-stack HTTP flow
# --------------------------------------------------------------------------- #
@pytest.fixture
def seeded(client):
    """A staff business + services, and a logged-in customer."""
    # staff user
    from src.accounts.adapters.outbound.hasher import DjangoPasswordHasher
    from src.accounts.domain.entities import ROLE_STAFF
    from src.accounts.models import UserModel

    UserModel.objects.create(
        email="staff@q.com",
        password=DjangoPasswordHasher().hash("password123"),
        role=ROLE_STAFF,
    )
    login_staff = client.post(
        "/api/auth/login",
        data={"email": "staff@q.com", "password": "password123"},
        content_type="application/json",
    )
    staff_token = login_staff.json()["tokens"]["access_token"]
    staff_headers = {"Authorization": f"Bearer {staff_token}"}

    biz = client.post(
        "/api/staff/businesses",
        data={"name": "Queue Co", "slug": "queue-co", "timezone": "Asia/Riyadh"},
        content_type="application/json",
        headers=staff_headers,
    )
    assert biz.status_code == 201, biz.content
    biz_id = biz.json()["id"]

    svc = client.post(
        "/api/services",
        data={"name": "Checkup", "ticket_prefix": "A", "avg_duration_sec": 600},
        content_type="application/json",
        headers=staff_headers,
    )
    assert svc.status_code == 201, svc.content
    service_id = svc.json()["id"]

    # customer
    reg = client.post(
        "/api/auth/register",
        data={"email": "cust@q.com", "password": "password123", "full_name": "Cust"},
        content_type="application/json",
    )
    assert reg.status_code == 201
    login_cust = client.post(
        "/api/auth/login",
        data={"email": "cust@q.com", "password": "password123"},
        content_type="application/json",
    )
    cust_token = login_cust.json()["tokens"]["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    return {
        "client": client,
        "biz_id": biz_id,
        "service_id": service_id,
        "staff_headers": staff_headers,
        "cust_headers": cust_headers,
    }


@pytest.mark.django_db
def test_join_call_start_complete_flow(seeded):
    client = seeded["client"]
    service_id = seeded["service_id"]
    staff_headers = seeded["staff_headers"]
    cust_headers = seeded["cust_headers"]

    joined = client.post(f"/api/services/{service_id}/join", headers=cust_headers)
    assert joined.status_code == 201, joined.content
    entry = joined.json()
    assert entry["ticket_code"] == "A-001"
    assert entry["status"] == STATUS_WAITING

    # duplicate join -> 409
    dup = client.post(f"/api/services/{service_id}/join", headers=cust_headers)
    assert dup.status_code == 409

    # staff calls the entry
    called = client.post(f"/api/staff/entries/{entry['id']}/call", headers=staff_headers)
    assert called.status_code == 200
    assert called.json()["status"] == STATUS_CALLED

    started = client.post(f"/api/staff/entries/{entry['id']}/start", headers=staff_headers)
    assert started.status_code == 200
    assert started.json()["status"] == STATUS_IN_PROGRESS

    completed = client.post(f"/api/staff/entries/{entry['id']}/complete", headers=staff_headers)
    assert completed.status_code == 200
    assert completed.json()["status"] == STATUS_SERVED


@pytest.mark.django_db
def test_wait_estimate_endpoint(seeded):
    client = seeded["client"]
    service_id = seeded["service_id"]
    cust_headers = seeded["cust_headers"]

    joined = client.post(f"/api/services/{service_id}/join", headers=cust_headers)
    entry = joined.json()
    wait = client.get(f"/api/queue/entries/{entry['id']}/wait", headers=cust_headers)
    assert wait.status_code == 200
    assert wait.json()["position"] == 1


@pytest.mark.django_db
def test_customer_cannot_access_other_ticket(seeded):
    client = seeded["client"]
    service_id = seeded["service_id"]

    # second customer
    client.post(
        "/api/auth/register",
        data={"email": "cust2@q.com", "password": "password123", "full_name": "C2"},
        content_type="application/json",
    )
    login2 = client.post(
        "/api/auth/login",
        data={"email": "cust2@q.com", "password": "password123"},
        content_type="application/json",
    )
    headers2 = {"Authorization": f"Bearer {login2.json()['tokens']['access_token']}"}

    joined = client.post(f"/api/services/{service_id}/join", headers=seeded["cust_headers"])
    other = client.get(f"/api/queue/entries/{joined.json()['id']}", headers=headers2)
    assert other.status_code == 403


@pytest.mark.django_db
def test_live_snapshot_cached(seeded):
    client = seeded["client"]
    slug = "queue-co"
    first = client.get(f"/api/businesses/{slug}/live")
    assert first.status_code == 200, first.content
    assert "services" in first.json()
