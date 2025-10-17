import re
import gpxpy
from typing import Annotated
from datetime import datetime, date
from fastapi import APIRouter, Depends, UploadFile, Form
from shapely.geometry import LineString
from geoalchemy2.shape import from_shape
from db.queries.trips import create_trip, get_trip, get_user_trips, delete_trip, update_trip
from db.queries.rides import create_ride
from db.schema import User, Ride, Trip
from app.models import TripModel, RideResponse
from app.config import config 
from app.dependencies import get_auth_user
from app.errors import UnauthorizedError, InvalidGPXError, InputError


trip_router = APIRouter(
    prefix="/trips",
    tags=["Trips"]
)

def generate_slug(text: str) -> str:
    slug = text.lower()
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug


@trip_router.post('/')
async def handler_create_trip(trip_data: TripModel, auth_user: Annotated[User, Depends(get_auth_user)]):
    
    slug = generate_slug(trip_data.title)
    
    new_trip = Trip(user_id = auth_user.id,
                    title = trip_data.title,
                    description = trip_data.description,
                    start_date = trip_data.start_date,
                    end_date= trip_data.end_date,
                    slug = slug
                    )
    
    return create_trip(new_trip)


@trip_router.post('/{trip_id}/upload')
async def handler_add_ride(
    trip_id: str, 
    notes: Annotated[str, Form()],
    date: Annotated[date, Form()],
    file: UploadFile,
    auth_user: Annotated[User, Depends(get_auth_user)],
    title: Annotated[str | None, Form()] = None) -> RideResponse:
    
    trip = get_trip(trip_id)
    
    if auth_user.id != trip.user_id:
        raise UnauthorizedError("Trip does not belong to user")
        
    if file.content_type not in ["multipart/form-data","application/gpx+xml", "application/xml", "text/xml", "application/octet-stream"] :
        raise Exception(f"Invalid content type header. Receveid: {file.content_type}")
        
    if not file.filename.endswith('.gpx'):
        raise Exception('Invalid file type. Supported types: .gpx')
    
    if file.size > config.limits.max_upload_size:
        raise Exception("Maximum file size exceeded. 50MB")
    
    if date < trip.start_date:
        raise InputError('Ride date cannot start before trip')

    
### Extract Data
    try:
        # Get route coordinates
        coords = []
        content = await file.read()
        gpx = gpxpy.parse(content) 
        
        if not gpx.tracks:
            raise InvalidGPXError("GPX file contains no tracks")

        for track in gpx.tracks:
            if not track.segments:
                raise InvalidGPXError("Track contains no segments")
            
            for segment in track.segments:
                if len(segment.points) < 10:
                    raise InvalidGPXError(f"Segment has insufficient points (found {len(segment.points)}, minimum 10 required)")
                    
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    coords.append((point.longitude, point.latitude))
        line = LineString(coords)
        linesting = from_shape(line, srid= 4326)
        
        # Get moving data
        moving_data = gpx.get_moving_data()
        distance = gpx.length_2d()
        ascent = gpx.get_uphill_downhill().uphill 
        high_point = gpx.get_elevation_extremes().maximum
        moving_time = moving_data.moving_time
        
        
        new_ride = Ride(
            trip_id = trip_id,
            notes = notes,
            date= date,
            distance= distance,
            elevation_gain= ascent,
            high_point = high_point,
            moving_time = moving_time,
            route = linesting,
            title = title
            )
        return create_ride(new_ride)
        
    except Exception as e:
        raise Exception("Error creating ride: ") from e
    
