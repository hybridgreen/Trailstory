import re
import gpxpy
from typing import Annotated
from datetime import datetime, date
from fastapi import APIRouter, Depends, UploadFile, Form
from shapely.geometry import LineString, Polygon
from shapely import bounds
from geoalchemy2.shape import from_shape, to_shape
from db.queries.trips import create_trip, get_trip, get_user_trips, delete_trip, update_trip
from db.queries.rides import create_ride, get_trip_rides_asc
from db.schema import User, Ride, Trip
from app.models import TripModel , RideResponse, TripDraft
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

def aggregate_trip(trip: Trip):
    rides = get_trip_rides_asc(trip.id)
    agg_route = []
    if rides:
        for ride in rides:
            agg_route.append(ride.route)
        return agg_route
    raise Exception("Error: No rides found in trip")

def generate_bounding_box(trip: Trip):
    
    if not trip.route:
        raise Exception("Error: Cannot generate bounding box. Trip has no route")
    coords = bounds(to_shape(trip.route)).tolist()
    box = Polygon([
        (coords[0], coords[1]),#   (min_x, min_y)  
        (coords[2], coords[1]),#   (max_x, min_y)
        (coords[2], coords[3]),#   (max_x, max_y)
        (coords[0], coords[3]),#   (min_x, max_y)
        (coords[0], coords[1])])#  (min_x, min_y)
    
    return from_shape(box, srid= 4326)
    
       

@trip_router.post('/')
async def handler_draft_trip(
    trip_data: Annotated[TripDraft, Form()],
    auth_user: Annotated[User, Depends(get_auth_user)]):
    
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
        raise UnauthorizedError("Error: Trip does not belong to user")
        
    if file.content_type not in ["multipart/form-data","application/gpx+xml", "application/xml", "text/xml", "application/octet-stream"] :
        raise InputError(f"Invalid content type header. Received: {file.content_type}")
        
    if not file.filename.endswith('.gpx'):
        raise InputError('Invalid file type. Supported types: .gpx')
    
    if file.size > config.limits.max_upload_size:
        raise InputError("Maximum file size exceeded. 50MB")
    
    if date < trip.start_date:
        raise InputError('Error: Ride date cannot start before trip')

    
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
        linestring = from_shape(line, srid= 4326)
        
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
            route = linestring,
            title = title
            )
        return create_ride(new_ride)
        
    except Exception as e:
        raise Exception(f"Error creating ride: {e}")


@trip_router.post('/{trip_id}/submit')
async def handler_save_trip(
    trip_id:str,
    form_data: Annotated[TripModel, Form()],
    auth_user: Annotated[User, Depends(get_auth_user)]
    ):
    trip = get_trip(trip_id)
    if(trip.user_id != auth_user.id):
        raise UnauthorizedError("Error: Trip does not belong to user")
    
    trip.route = aggregate_trip(trip)
    trip.bounding_box = generate_bounding_box(trip) 
    
