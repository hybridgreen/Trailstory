from fastapi.testclient import TestClient
from app.main import app
import pytest
from app.config import config
from pathlib import Path

client = TestClient(app)

tests_dir = Path(__file__).parent.parent
samples_dir = tests_dir.joinpath("./samples")

ride1_path = samples_dir.joinpath("ride1.gpx")
ride2_path = samples_dir.joinpath("ride2.gpx")
ride3_path = samples_dir.joinpath("ride3.gpx")
not_enough = samples_dir.joinpath("not_enough.gpx")
invalid_ride = samples_dir.joinpath("invalid.gpx")


def reset():
    client.post(
        "/admin/reset", headers={"Authorization": f"Bearer {config.auth.admin_token}"}
    )


@pytest.fixture(scope="function")
def user():
    reset()
    fakeUser = {
        "email": "sample@pineapple.com",
        "username": "spongebob",
        "password": "YourNameIs123!",
    }

    user = client.post("/users", data=fakeUser)
    user_data = user.json()
    return user_data


@pytest.fixture(scope="function")
def trip(user):
    at = user["access_token"]

    fake_trip = {
        "title": "The Lanna Kingdom",
        "description": "The Lanna Kingdom is a 393-kilometer bikepacking loop based in Northern Thailand. Starting in Chiang Mai, it weaves riders through a crocheted masterpiece of tropical terrain, from dusty dirt roads and vibrant forest trails to banana plantations and elephant grazing grounds. Mix in delicious food, brilliant sunrises, gracious locals, abundant camping, and unique hill tribe cultures, and it’s easy to see why Thailand is known as the land of smiles.",
        "start_date": "2025-12-01",
    }

    trip = client.post(
        "/trips", data=fake_trip, headers={"Authorization": f"Bearer {at}"}
    )

    trip_data = trip.json()
    return trip_data


def test_draft_trip(user):
    at = user["access_token"]

    fake_trip = {
        "title": "The Lanna Kingdom",
        "description": "The Lanna Kingdom is a 393-kilometer bikepacking loop based in Northern Thailand. Starting in Chiang Mai, it weaves riders through a crocheted masterpiece of tropical terrain, from dusty dirt roads and vibrant forest trails to banana plantations and elephant grazing grounds. Mix in delicious food, brilliant sunrises, gracious locals, abundant camping, and unique hill tribe cultures, and it’s easy to see why Thailand is known as the land of smiles.",
        "start_date": "2025-12-01",
    }

    trip = client.post(
        "/trips", data=fake_trip, headers={"Authorization": f"Bearer {at}"}
    )

    trip_data = trip.json()
    assert trip.status_code == 201
    assert trip_data["title"] == fake_trip["title"]
    assert trip_data["start_date"] == fake_trip["start_date"]


def test_delete_trip(user, trip):
    at = user["access_token"]
    trip_id = trip["id"]

    f1 = open(ride1_path, "rb")
    f2 = open(ride2_path, "rb")
    f3 = open(ride3_path, "rb")

    response = client.post(
        f"/trips/{trip_id}/upload/multi",
        files=[
            ("files", ("ride1.gpx", f1, "application/gpx+xml")),
            ("files", ("ride2.gpx", f2, "application/gpx+xml")),
            ("files", ("ride3.gpx", f3, "application/gpx+xml")),
        ],
        headers={"Authorization": f"Bearer {at}"},
    )
    f1.close()
    f2.close()
    f3.close()

    response = client.delete(
        f"/trips/{trip_id}", headers={"Authorization": f"Bearer {at}"}
    )

    assert response.status_code == 204

    rides_response = client.get(f"/trips/{trip_id}/rides")

    rides = rides_response.json()
    assert len(rides) == 0


def test_delete_trip_unauth(trip):
    trip_id = trip["id"]
    response = client.delete(
        f"/trips/{trip_id}",
        headers={"Authorization": f"Bearer {5839405149865139805690346}"},
    )

    assert response.status_code == 401


def test_submit_trip_no_rides(user, trip):
    at = user["access_token"]
    trip_id = trip["id"]

    final_trip = {
        "title": "The Lanna Kingdom",
        "description": "Test Trip",
        "start_date": "2025-12-01",
        "end_date": "2025-12-01",
        "is_published": True,
    }

    response = client.put(
        f"/trips/{trip_id}", data=final_trip, headers={"Authorization": f"Bearer {at}"}
    )

    assert response.status_code == 500


def test_submit_deleted_trip(user, trip):
    at = user["access_token"]
    trip_id = trip["id"]

    final_trip = {
        "title": "The Lanna Kingdom",
        "description": "Test Trip",
        "start_date": "2025-12-01",
        "end_date": "2025-12-01",
        "is_published": True,
    }

    response = client.delete(
        f"/trips/{trip_id}", headers={"Authorization": f"Bearer {at}"}
    )

    response = client.put(
        f"/trips/{trip_id}/submit",
        data=final_trip,
        headers={"Authorization": f"Bearer {at}"},
    )

    assert response.status_code == 404


# Start Date after end date
def test_submit_invalid_trip(user, trip):
    at = user["access_token"]
    trip_id = trip["id"]

    final_trip = {
        "title": "The Lanna Kingdom",
        "description": "Test Trip",
        "start_date": "2025-12-01",
        "end_date": "2024-12-01",
        "is_published": True,
    }

    response = client.put(
        f"/trips/{trip_id}", data=final_trip, headers={"Authorization": f"Bearer {at}"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Error: End date cannot be before start date"


def test_slug_generation():
    """Test slug handles special characters and spaces correctly"""
    from app.routers.trips import generate_slug

    assert generate_slug("My Trip") == "my-trip"

    assert generate_slug("The   Lanna    Kingdom") == "the-lanna-kingdom"

    assert generate_slug("Trip #1: Mountain's Edge!") == "trip-1-mountains-edge"

    assert generate_slug("north_coast_ride") == "north-coast-ride"

    assert generate_slug("  Trip Name  ") == "trip-name"

    assert generate_slug("ride---one") == "ride-one"

    assert generate_slug("Trip 🚴 2024") == "trip-2024"

    assert generate_slug("   ") == ""
    assert generate_slug("!!!") == ""


reset()
