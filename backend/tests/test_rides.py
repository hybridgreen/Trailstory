from fastapi.testclient import TestClient
from app.main import app
import pytest
from app.config import config
from pathlib import Path
import json

client = TestClient(app)

tests_dir = Path(__file__).parent.parent
samples_dir = tests_dir.joinpath("./samples")

ride1_path = samples_dir.joinpath("ride1.gpx")
ride2_path = samples_dir.joinpath("ride2.gpx")
ride3_path = samples_dir.joinpath("ride3.gpx")
not_enough = samples_dir.joinpath("not_enough.gpx")
no_tracks_ride = samples_dir.joinpath("no_tracks.gpx")
no_timestamps = samples_dir.joinpath("no_timestamps.gpx")
low_points = samples_dir.joinpath("not_enough.gpx")
two_segments = samples_dir.joinpath("two_segments.gpx")
no_segments = samples_dir.joinpath("no_segments.gpx")


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


def test_add_ride(user, trip):
    at = user["access_token"]
    trip_id = trip["id"]

    with open(ride1_path, "rb") as f:
        response = client.post(
            f"/trips/{trip_id}/rides",
            files=[("files", ("ride1.gpx", f, "application/gpx+xml"))],
            headers={"Authorization": f"Bearer {at}"},
        )
        ride_data = response.json()[0]

    assert response.status_code == 201
    assert ride_data["distance"] == 921.0259820926173
    assert ride_data["trip_id"] == trip_id


def test_add_ride_invalid_xml(user, trip):
    trip_id = trip["id"]
    at = user["access_token"]

    with open(no_tracks_ride, "rb") as f:
        response = client.post(
            f"/trips/{trip_id}/rides",
            files=[("files", ("ride1.gpx", f, "application/gpx+xml"))],
            headers={"Authorization": f"Bearer {at}"},
        )
        error = response.json()
        detail: str = error["detail"]
    assert response.status_code == 400
    assert "detail" in error
    assert "GPX file contains no tracks" in detail


def test_add_ride_invalid_gpx(user, trip):
    trip_id = trip["id"]
    at = user["access_token"]

    with open(ride1_path, "rb") as f:
        response = client.post(
            f"/trips/{trip_id}/rides",
            files=[("files", ("ride1", f, "application/gpx+xml"))],
            headers={"Authorization": f"Bearer {at}"},
        )
        error = response.json()
        detail: str = error["detail"]
    assert response.status_code == 400
    assert "detail" in error
    assert "Invalid file type" in detail


def test_add_ride_insufficient_points(user, trip):
    trip_id = trip["id"]
    at = user["access_token"]

    with open(not_enough, "rb") as f:
        response = client.post(
            f"/trips/{trip_id}/rides",
            files=[("files", ("ride1.gpx", f, "application/gpx+xml"))],
            headers={"Authorization": f"Bearer {at}"},
        )
        error = response.json()
        detail: str = error["detail"]

    assert response.status_code == 400
    assert "detail" in error
    assert "insufficient points" in detail


def test_add_rides(user, trip):
    trip_id = trip["id"]
    at = user["access_token"]

    f1 = open(ride1_path, "rb")
    f2 = open(ride2_path, "rb")
    f3 = open(ride3_path, "rb")

    response = client.post(
        f"/trips/{trip_id}/rides",
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
    assert response.status_code >= 200


def test_ride_aggregation(user, trip):
    trip_id = trip["id"]
    at = user["access_token"]

    trip_id = trip["id"]
    at = user["access_token"]

    f1 = open(ride1_path, "rb")
    f2 = open(ride2_path, "rb")
    f3 = open(ride3_path, "rb")

    response = client.post(
        f"/trips/{trip_id}/rides",
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

    trip_data = {
        "title": "Test Aggregation",
        "description": "Testing",
        "start_date": "2025-01-12",
        "end_date": "2025-01-14",
        "is_published": "True",
    }

    response = client.put(
        f"/trips/{trip_id}", data=trip_data, headers={"Authorization": f"Bearer {at}"}
    )

    aggregated = response.json()
    print(aggregated)

    # Expected totals from GPX files
    # Ride 1: ~921m distance, 22m elevation, high 62m
    # Ride 2: ~1048m distance, 147m elevation, high 212m
    # Ride 3: ~1314m distance, 5m elevation, high 10m

    rides = client.get(f"/trips/{trip_id}/rides").json()
    expected_distance = (
        rides[0]["distance"] + rides[1]["distance"] + rides[2]["distance"]
    )  # Approximate
    expected_elevation = (
        rides[0]["elevation_gain"]
        + rides[1]["elevation_gain"]
        + rides[2]["elevation_gain"]
    )
    expected_high = 212.0

    assert response.status_code >= 200
    assert abs(aggregated["total_distance"] - expected_distance) < 50  # Allow margin
    assert abs(aggregated["total_elevation"] - expected_elevation) < 5
    assert aggregated["high_point"] == expected_high
    assert "route" in aggregated
    assert "bounding_box" in aggregated


def test_bounding_box_coverage(user, trip):
    """Verify bounding box encompasses all ride coordinates"""

    trip_id = trip["id"]
    at = user["access_token"]

    f1 = open(ride1_path, "rb")
    f2 = open(ride2_path, "rb")

    response = client.post(
        f"/trips/{trip_id}/rides",
        files=[
            ("files", ("ride1.gpx", f1, "application/gpx+xml")),
            ("files", ("ride2.gpx", f2, "application/gpx+xml")),
        ],
        headers={"Authorization": f"Bearer {at}"},
    )
    f1.close()
    f2.close()

    trip_data = {
        "title": "Bounding Box Test",
        "description": "Testing",
        "start_date": "2025-01-12",
        "end_date": "2025-01-13",
        "is_published": "True",
    }

    response = client.put(
        f"/trips/{trip_id}", data=trip_data, headers={"Authorization": f"Bearer {at}"}
    )
    assert response.status_code == 200

    trip_result = response.json()

    bbox = trip_result["bounding_box"]

    bbox_geom = json.loads(bbox)
    coords = bbox_geom["coordinates"][0]

    # Extract min/max from bbox
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)

    # Parse ride routes and check they're within bounds
    rides = client.get(f"/trips/{trip_id}/rides").json()
    route1 = json.loads(rides[0]["route"])
    route2 = json.loads(rides[1]["route"])

    for coord in route1["coordinates"]:
        assert min_lon <= coord[0] <= max_lon
        assert min_lat <= coord[1] <= max_lat

    for coord in route2["coordinates"]:
        assert min_lon <= coord[0] <= max_lon
        assert min_lat <= coord[1] <= max_lat
