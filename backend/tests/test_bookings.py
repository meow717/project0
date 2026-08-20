"""End-to-end tests for the bookings feature (use cases + HTTP API)."""

from datetime import UTC, datetime, timedelta

import pytest


@pytest.fixture
def seeded(client):
    from src.accounts.adapters.outbound.hasher import DjangoPasswordHasher
    from src.accounts.domain.entities import ROLE_STAFF
    from src.accounts.models import UserModel

    UserModel.objects.create(
        email="staff@b.com",
        password=DjangoPasswordHasher().hash("password123"),
        role=ROLE_STAFF,
    )
    login = client.post(
        "/api/auth/login",
        data={"email": "staff@b.com", "password": "password123"},
        content_type="application/json",
    )
    staff_headers = {"Authorization": f"Bearer {login.json()['tokens']['access_token']}"}

    biz = client.post(
        "/api/staff/businesses",
        data={"name": "Book Co", "slug": "book-co", "timezone": "Asia/Riyadh"},
        content_type="application/json",
        headers=staff_headers,
    )
    biz_id = biz.json()["id"]

    svc = client.post(
        "/api/services",
        data={"name": "Consult", "ticket_prefix": "C", "avg_duration_sec": 900},
        content_type="application/json",
        headers=staff_headers,
    )
    service_id = svc.json()["id"]

    client.post(
        "/api/auth/register",
        data={"email": "cust@b.com", "password": "password123", "full_name": "C"},
        content_type="application/json",
    )
    login_cust = client.post(
        "/api/auth/login",
        data={"email": "cust@b.com", "password": "password123"},
        content_type="application/json",
    )
    cust_headers = {"Authorization": f"Bearer {login_cust.json()['tokens']['access_token']}"}

    return {
        "client": client,
        "biz_id": biz_id,
        "service_id": service_id,
        "staff_headers": staff_headers,
        "cust_headers": cust_headers,
    }


@pytest.mark.django_db
def test_create_and_cancel_booking(seeded):
    client = seeded["client"]
    biz_id = seeded["biz_id"]
    service_id = seeded["service_id"]
    cust_headers = seeded["cust_headers"]

    scheduled = (datetime.now(UTC) + timedelta(days=1)).replace(hour=10, minute=0)
    resp = client.post(
        "/api/bookings",
        data={
            "business_id": biz_id,
            "service_id": service_id,
            "scheduled_at": scheduled.isoformat(),
            "notes": "First visit",
        },
        content_type="application/json",
        headers=cust_headers,
    )
    assert resp.status_code == 201, resp.content
    booking = resp.json()
    assert booking["status"] == "pending"

    mine = client.get("/api/bookings/mine", headers=cust_headers)
    assert mine.status_code == 200
    assert len(mine.json()) == 1

    cancelled = client.delete(f"/api/bookings/{booking['id']}", headers=cust_headers)
    assert cancelled.status_code == 204


@pytest.mark.django_db
def test_overlapping_booking_rejected(seeded):
    client = seeded["client"]
    biz_id = seeded["biz_id"]
    service_id = seeded["service_id"]
    cust_headers = seeded["cust_headers"]

    scheduled = (datetime.now(UTC) + timedelta(days=2)).replace(hour=10, minute=0)
    data = {
        "business_id": biz_id,
        "service_id": service_id,
        "scheduled_at": scheduled.isoformat(),
    }
    first = client.post(
        "/api/bookings", data=data, content_type="application/json", headers=cust_headers
    )
    assert first.status_code == 201

    # Same slot + same user -> 409
    second = client.post(
        "/api/bookings", data=data, content_type="application/json", headers=cust_headers
    )
    assert second.status_code == 409


@pytest.mark.django_db
def test_staff_confirms_booking(seeded):
    client = seeded["client"]
    biz_id = seeded["biz_id"]
    service_id = seeded["service_id"]
    cust_headers = seeded["cust_headers"]
    staff_headers = seeded["staff_headers"]

    scheduled = (datetime.now(UTC) + timedelta(days=3)).replace(hour=9, minute=0)
    created = client.post(
        "/api/bookings",
        data={
            "business_id": biz_id,
            "service_id": service_id,
            "scheduled_at": scheduled.isoformat(),
        },
        content_type="application/json",
        headers=cust_headers,
    )
    booking_id = created.json()["id"]

    confirmed = client.patch(
        f"/api/staff/bookings/{booking_id}",
        data={"status": "confirmed"},
        content_type="application/json",
        headers=staff_headers,
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "confirmed"
