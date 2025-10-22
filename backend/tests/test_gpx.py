from fastapi.exceptions import ValidationException
from fastapi import UploadFile
from app.main import app
import pytest
from app.errors import *
from app.config import config
from pathlib import Path
from app.routers.trips import extract_gpx_data, validate_gpx_upload
from io import BytesIO


tests_dir = Path(__file__).parent.parent # /Users/yasseryaya-oye/workspace/hybridgreen/Trailstory/backend/tests
samples_dir =tests_dir.joinpath('../samples') #/Users/yasseryaya-oye/workspace/hybridgreen/Trailstory/samples/ride1.gpx

ride1_path = samples_dir.joinpath('ride1.gpx')
invalid_ride = samples_dir.joinpath('invalid.gpx')
no_tracks_ride = samples_dir.joinpath('no_tracks.gpx')
no_timestamps = samples_dir.joinpath('no_timestamps.gpx')
low_points = samples_dir.joinpath('not_enough.gpx')
two_segments = samples_dir.joinpath('two_segments.gpx')
no_segments = samples_dir.joinpath('no_segments.gpx')



def test_valid_ride():
    with open(ride1_path, 'rb') as f:
        upload = UploadFile(
            filename= 'ride1.gpx',
            file=f,
            headers={'content-type':'text/xml'},
            size= 1 * 1024
            )
        file_content = f.read()
        
        result = validate_gpx_upload(upload)
        ride = extract_gpx_data(trip_id= 1234, content= file_content)
        
        assert result == True
        assert str(ride.date) == '2025-01-12'
        assert 921* 0.95 < ride.distance < 921* 1.05
        
def test_empty_file():
        
        file_content = b"some bytes"
        f = BytesIO(file_content)
        
        upload = UploadFile(
            filename= 'ride1.gpx',
            file=f,
            headers={'content-type':'text/xml'},
            size= 0
            )
        with pytest.raises(InputError) as excinfo:
            result = validate_gpx_upload(upload)
            
        assert "empty" in str(excinfo.value)
        
def test_invalid_filetype():
        
        file_content = b"some bytes"
        f = BytesIO(file_content)
        
        upload = UploadFile(
            filename= 'ride1',
            file=f,
            headers={'content-type':'text/xml'},
            size= 1024
            )
        with pytest.raises(InputError) as excinfo:
            result = validate_gpx_upload(upload)
            
        assert "Invalid file type" in str(excinfo.value)
        assert "ride1" in str(excinfo.value)
        
def test_invalid_content_type():
        
        file_content = b"some bytes"
        f = BytesIO(file_content)
        
        upload = UploadFile(
            filename= 'ride1.gpx',
            file=f,
            headers={'content-type':'txt/xml'},
            size= 1024
            )
        with pytest.raises(InputError) as excinfo:
            result = validate_gpx_upload(upload)
            
        assert "Invalid content type" in str(excinfo.value)
        assert "txt" in str(excinfo.value)
        
def test_large_file():
        
        file_content = b"some bytes"
        f = BytesIO(file_content)
        
        upload = UploadFile(
            filename= 'ride1.gpx',
            file=f,
            headers={'content-type':'text/xml'},
            size= 50 * 1024 * 1024
            )
        with pytest.raises(InputError) as excinfo:
            result = validate_gpx_upload(upload)
            
        assert "Maximum file size exceeded" in str(excinfo.value)

def test_file_size_limit():
        
        file_content = b"some bytes"
        f = BytesIO(file_content)
        
        upload = UploadFile(
            filename= 'ride1.gpx',
            file=f,
            headers={'content-type':'text/xml'},
            size= 15 * 1024 * 1024
            )
        
        result = validate_gpx_upload(upload)
            
        assert result == True
        
def test_no_tracks_ride():
    with open(no_tracks_ride, 'rb') as f:
        upload = UploadFile(
            filename= 'ride1.gpx',
            file=f,
            headers={'content-type':'text/xml'},
            size= 1 * 1024
            )
        file_content = f.read()
        
        with pytest.raises(InvalidGPXError) as exc:
            ride = extract_gpx_data(trip_id= 1234, content= file_content)
        
        assert "no tracks" in str(exc.value)

def test_no_segments_ride():
    with open(no_segments, 'rb') as f:
        upload = UploadFile(
            filename= 'ride1.gpx',
            file=f,
            headers={'content-type':'text/xml'},
            size= 1 * 1024
            )
        file_content = f.read()
        
        with pytest.raises(InvalidGPXError) as exc:
            ride = extract_gpx_data(trip_id= 1234, content= file_content)
        
        assert "no segments" in str(exc.value)

def test_no_timestamps_ride():
    with open(no_timestamps, 'rb') as f:
        upload = UploadFile(
            filename= 'ride1.gpx',
            file=f,
            headers={'content-type':'text/xml'},
            size= 1 * 1024
            )
        file_content = f.read()
        
        with pytest.raises(InvalidGPXError) as exc:
            ride = extract_gpx_data(trip_id= 1234, content= file_content)
        
        assert "timestamps" in str(exc.value)
        
def test_not_enough_ride():
    with open(low_points, 'rb') as f:
        upload = UploadFile(
            filename= 'ride1.gpx',
            file=f,
            headers={'content-type':'text/xml'},
            size= 1 * 1024
            )
        file_content = f.read()
        
        with pytest.raises(InvalidGPXError) as exc:
            ride = extract_gpx_data(trip_id= 1234, content= file_content)
        
        assert "insufficient points" in str(exc.value)

def test_not_enough_ride():
    with open(two_segments, 'rb') as f:
        upload = UploadFile(
            filename= 'ride1.gpx',
            file=f,
            headers={'content-type':'text/xml'},
            size= 1 * 1024
            )
        file_content = f.read()
        
        with pytest.raises(InvalidGPXError) as exc:
            ride = extract_gpx_data(trip_id= 1234, content= file_content)
        
        assert "multiple tracks" in str(exc.value)