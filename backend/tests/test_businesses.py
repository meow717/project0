"""End-to-end tests for the businesses feature (use cases + HTTP API)."""

import pytest
from django.test import Client

from src.accounts.domain.entities import ROLE_STAFF
from src.accounts.models import UserModel
from src.businesses.application.use_cases import (
    CreateBusinessCommand,
)
from src.businesses.container import container
from src.businesses.domain.exceptions import SlugAlreadyUsed


@pytest.fixture
def staff_user(db):
    from src.accounts.adapters.outbound.hasher import DjangoPasswordHasher

    user = UserModel.objects.create(
        email="staff@x.com",
        password=DjangoPasswordHasher().hash("password123"),
        role=ROLE_STAFF,
    )
    return user


@pytest.mark.django_db
def test_create_business_promotes_owner(staff_user):
    c = container()
    cmd = CreateBusinessCommand(
        name="Dental Clinic",
        slug="dental-clinic",
        created_by=staff_user.id,
        timezone="Asia/Riyadh",
    )
    biz = c.create_business(cmd)
    assert biz.id is not None
    assert biz.slug == "dental-clinic"

    staff_user.refresh_from_db()
    assert staff_user.role == ROLE_STAFF
    assert staff_user.business_id == biz.id


@pytest.mark.django_db
def test_duplicate_slug_rejected(staff_user):
    c = container()
    c.create_business(CreateBusinessCommand(name="A", slug="dup", created_by=staff_user.id))
    with pytest.raises(SlugAlreadyUsed):
        c.create_business(CreateBusinessCommand(name="B", slug="DUP", created_by=staff_user.id))


@pytest.mark.django_db
def test_search_filters_by_query(staff_user):
    c = container()
    c.create_business(
        CreateBusinessCommand(name="Heart Center", slug="heart", created_by=staff_user.id)
    )
    c.create_business(
        CreateBusinessCommand(name="Dental", slug="dental", created_by=staff_user.id)
    )
    result = c.search_businesses.execute(("dent", "", "", 1, 10))
    assert result.total == 1
    assert result.items[0].name == "Dental"


@pytest.mark.django_db
def test_search_filters_by_area_and_category(staff_user):
    c = container()
    c.create_business(
        CreateBusinessCommand(
            name="Clinic A",
            slug="clinic-a",
            created_by=staff_user.id,
            area="المنصور",
            category="مستشفيات",
        )
    )
    c.create_business(
        CreateBusinessCommand(
            name="Bank B",
            slug="bank-b",
            created_by=staff_user.id,
            area="الحارثية",
            category="بنوك",
        )
    )
    by_area = c.search_businesses.execute(("", "المنصور", "", 1, 10))
    assert by_area.total == 1
    assert by_area.items[0].slug == "clinic-a"

    by_category = c.search_businesses.execute(("", "", "بنوك", 1, 10))
    assert by_category.total == 1
    assert by_category.items[0].slug == "bank-b"

    combined = c.search_businesses.execute(("", "المنصور", "بنوك", 1, 10))
    assert combined.total == 0

    no_match = c.search_businesses.execute(("", "زيونة", "", 1, 10))
    assert no_match.total == 0


@pytest.mark.django_db
def test_api_business_lifecycle(staff_user):
    client = Client()
    # Login as staff to get a token.
    login = client.post(
        "/api/auth/login",
        data={"email": "staff@x.com", "password": "password123"},
        content_type="application/json",
    )
    assert login.status_code == 200
    token = login.json()["tokens"]["access_token"]
    auth = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/staff/businesses",
        data={
            "name": "Gov Office",
            "slug": "gov-office",
            "timezone": "Asia/Riyadh",
            "opens_at": "08:00",
            "closes_at": "16:00",
        },
        content_type="application/json",
        headers=auth,
    )
    assert created.status_code == 201, created.content
    biz = created.json()

    listed = client.get("/api/businesses?search=gov")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    detail = client.get(f"/api/businesses/{biz['slug']}")
    assert detail.status_code == 200
    assert detail.json()["name"] == "Gov Office"

    updated = client.put(
        f"/api/staff/businesses/{biz['id']}",
        data={"description": "Renovated"},
        content_type="application/json",
        headers=auth,
    )
    assert updated.status_code == 200
    assert updated.json()["description"] == "Renovated"


@pytest.mark.django_db
def test_any_authenticated_user_can_create_business():
    client = Client()
    reg = client.post(
        "/api/auth/register",
        data={"email": "cust@x.com", "password": "password123", "full_name": "C"},
        content_type="application/json",
    )
    assert reg.status_code == 201
    login = client.post(
        "/api/auth/login",
        data={"email": "cust@x.com", "password": "password123"},
        content_type="application/json",
    )
    token = login.json()["tokens"]["access_token"]

    # A customer can create a business (which promotes them to staff).
    resp = client.post(
        "/api/staff/businesses",
        data={"name": "X", "slug": "x", "timezone": "Asia/Riyadh"},
        content_type="application/json",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.content

    # ...but not manage services until they refresh (token role is customer).
    svc = client.post(
        "/api/services",
        data={"name": "S", "ticket_prefix": "A"},
        content_type="application/json",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert svc.status_code == 403
