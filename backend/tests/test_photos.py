from fastapi.testclient import TestClient
from app.main import app
import pytest
from app.config import config
from pathlib import Path


client = TestClient(app)
tests_dir = Path(__file__).parent.parent
samples_dir = tests_dir.joinpath("./samples")
photos_dir = samples_dir / "photos"


def reset():
    client.post(
        "/admin/reset", headers={"Authorization": f"Bearer {config.auth.admin_token}"}
    )


@pytest.fixture(scope="function")
def setup():
    reset()

    test_user = {
        "email": "samle@pineapple.com",
        "username": "spongebob",
        "password": "YourNameIs123!",
    }
    user = client.post("/users", data=test_user)
    user_response = user.json()

    at = user_response["access_token"]

    test_trip = {
        "title": "The Lanna Kingdom",
        "description": "390km in Thailand.",
        "start_date": "2025-12-01",
    }

    trip = client.post(
        "/trips", data=test_trip, headers={"Authorization": f"Bearer {at}"}
    )

    trip_data = trip.json()
    trip_id = trip_data["id"]

    ride1_path = samples_dir.joinpath("ride1.gpx")
    ride2_path = samples_dir.joinpath("ride2.gpx")
    ride3_path = samples_dir.joinpath("ride3.gpx")

    f1 = open(ride1_path, "rb")
    f2 = open(ride2_path, "rb")
    f3 = open(ride3_path, "rb")

    client.post(
        f"/trips/{trip_id}/rides/",
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

    return user_response, trip_data


def test_add_photos(setup):
    user_response, trip_data = setup
    at = user_response["access_token"]
    trip_id = trip_data["id"]

    file_paths = [f for f in Path(photos_dir).iterdir() if f.is_file()]

    files = []
    file_handles = []

    for file in file_paths:
        f = open(file, "rb")
        content = f.read()
        file_handles.append(f)
        files.append(("files", (file.name, content, "image/jpeg")))

    try:
        response = client.post(
            f"/trips/{trip_id}/photos",
            files=files,
            headers={"Authorization": f"Bearer {at}"},
        )

        if response.status_code != 201:
            print(response.json())

        links = response.json()["links"]
        print(links)

        assert response.status_code == 201
        assert len(links) == len(file_paths)

    finally:
        for f in file_handles:
            f.close()


def test_add_wrong_mime(setup):
    user_response, trip_data = setup
    at = user_response["access_token"]
    trip_id = trip_data["id"]

    file_paths = [f for f in Path(photos_dir).iterdir() if f.is_file()]

    files = []

    for file in file_paths:
        with open(file, "rb") as f:
            content = f.read()
            files.append(("files", (file.name, content, "image/jp")))

    response = client.post(
        f"/trips/{trip_id}/photos",
        files=files,
        headers={"Authorization": f"Bearer {at}"},
    )

    assert response.status_code == 400


def test_add_avatar(setup):
    user_response, trip_data = setup
    at = user_response["access_token"]

    file_path = photos_dir / "avatar.jpg"

    files = []
    file_handles = []

    f = open(file_path, "rb")
    content = f.read()
    file_handles.append(f)
    files.append(("file", (f.name, content, "image/jpeg")))

    try:
        response = client.post(
            "/users/avatar/", files=files, headers={"Authorization": f"Bearer {at}"}
        )

        photos = response.json()

        if response.status_code != 201:
            print(photos)
        assert response.status_code == 201

    finally:
        f.close()
