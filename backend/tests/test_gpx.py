from fastapi import UploadFile
import pytest
from app.errors import InputError, InvalidGPXError
from pathlib import Path
from app.routers.trips import extract_gpx_data, validate_gpx_upload
from io import BytesIO


tests_dir = Path(__file__).parent.parent
samples_dir = tests_dir.joinpath("./samples")
ride1_path = samples_dir.joinpath("ride1.gpx")
no_tracks_ride = samples_dir.joinpath("no_tracks.gpx")
no_timestamps = samples_dir.joinpath("no_timestamps.gpx")
low_points = samples_dir.joinpath("not_enough.gpx")
two_segments = samples_dir.joinpath("two_segments.gpx")
no_segments = samples_dir.joinpath("no_segments.gpx")


def test_valid_ride():
    with open(ride1_path, "rb") as f:
        upload = UploadFile(
            filename="ride1.gpx",
            file=f,
            headers={"content-type": "text/xml;charset=utf-8"},
            size=1 * 1024,
        )
        file_content = f.read()

        result = validate_gpx_upload(upload)
        ride = extract_gpx_data(trip_id=1234, content=file_content)

        assert result
        assert "2025-01-12" in str(ride.date)
        assert 921 * 0.95 < ride.distance < 921 * 1.05


def test_empty_file():
    file_content = b"some bytes"
    f = BytesIO(file_content)

    upload = UploadFile(
        filename="ride1.gpx",
        file=f,
        headers={"content-type": "text/xml;charset=utf-8"},
        size=0,
    )
    with pytest.raises(InputError) as excinfo:
        validate_gpx_upload(upload)

    assert "empty" in str(excinfo.value)


def test_invalid_filetype():
    file_content = b"some bytes"
    f = BytesIO(file_content)

    upload = UploadFile(
        filename="ride1",
        file=f,
        headers={"content-type": "text/xml;charset=utf-8"},
        size=1024,
    )
    with pytest.raises(InputError) as excinfo:
        validate_gpx_upload(upload)

    assert "Invalid file type" in str(excinfo.value)
    assert "ride1" in str(excinfo.value)


def test_invalid_content_type():
    file_content = b"some bytes"
    f = BytesIO(file_content)

    upload = UploadFile(
        filename="ride1.gpx", file=f, headers={"content-type": "txt/xml"}, size=1024
    )
    with pytest.raises(InputError) as excinfo:
        validate_gpx_upload(upload)

    assert "Invalid content type" in str(excinfo.value)
    assert "txt" in str(excinfo.value)


def test_large_file():
    file_content = b"some bytes"
    f = BytesIO(file_content)

    upload = UploadFile(
        filename="ride1.gpx",
        file=f,
        headers={"content-type": "text/xml;charset=utf-8"},
        size=50 * 1024 * 1024,
    )
    with pytest.raises(InputError) as excinfo:
        validate_gpx_upload(upload)

    assert "Maximum file size exceeded" in str(excinfo.value)


def test_file_size_limit():
    file_content = b"some bytes"
    f = BytesIO(file_content)

    upload = UploadFile(
        filename="ride1.gpx",
        file=f,
        headers={"content-type": "text/xml;charset=utf-8"},
        size=15 * 1024 * 1024,
    )

    result = validate_gpx_upload(upload)

    assert result


def test_no_tracks_ride():
    with open(no_tracks_ride, "rb") as f:
        file_content = f.read()
        with pytest.raises(InvalidGPXError) as exc:
            extract_gpx_data(trip_id=1234, content=file_content)

        assert "no tracks" in str(exc.value)


def test_no_segments_ride():
    with open(no_segments, "rb") as f:
        file_content = f.read()

        with pytest.raises(InvalidGPXError) as exc:
            extract_gpx_data(trip_id=1234, content=file_content)

        assert "no segments" in str(exc.value)


def test_no_timestamps_ride():
    with open(no_timestamps, "rb") as f:
        file_content = f.read()

        with pytest.raises(InvalidGPXError) as exc:
            extract_gpx_data(trip_id=1234, content=file_content)

        assert "timestamps" in str(exc.value)


def test_not_enough_ride():
    with open(low_points, "rb") as f:
        file_content = f.read()

        with pytest.raises(InvalidGPXError) as exc:
            extract_gpx_data(trip_id=1234, content=file_content)

        assert "insufficient points" in str(exc.value)


def test_multiple_segments():
    with open(two_segments, "rb") as f:
        file_content = f.read()

        with pytest.raises(InvalidGPXError) as exc:
            extract_gpx_data(trip_id=1234, content=file_content)

        assert "multiple tracks" in str(exc.value)
