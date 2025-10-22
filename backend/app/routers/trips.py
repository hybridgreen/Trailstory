import re
import gpxpy
from typing import Annotated
from datetime import date
from fastapi import APIRouter, Depends, UploadFile, Form
from shapely.geometry import LineString, Polygon
from shapely import bounds, to_geojson
from geoalchemy2.shape import from_shape, to_shape
from db.queries.trips import create_trip, get_trip, delete_trip, update_trip
from db.queries.rides import create_ride, get_trip_rides_asc, create_rides, get_ride, update_ride
from db.schema import User, Ride, Trip
from app.models import TripModel , RideResponse, TripDraft, TripsResponse, TripResponse, RideModel
from app.config import config 
from app.dependencies import get_auth_user
from app.errors import UnauthorizedError, InvalidGPXError, InputError, ServerError

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
    distance = 0.0
    elevation = 0.0
    high_point = float('-inf')
    if not rides:
        raise ServerError("Error: No rides found in trip")
    
    for ride in rides:
        agg_route.extend(list(to_shape(ride.route).coords))
        distance += ride.distance
        elevation += ride.elevation_gain
        if ride.high_point > high_point:
            high_point = ride.high_point
    route = LineString(agg_route)
    return route, distance, elevation, high_point

def generate_bounding_box(route):
    
    coords = bounds(route).tolist()
    
    box = Polygon([
        (coords[0], coords[1]),#   (min_x, min_y)  
        (coords[2], coords[1]),#    (max_x, min_y)
        (coords[2], coords[3]),#   (max_x, max_y)
        (coords[0], coords[3]),#   (min_x, max_y)
        (coords[0], coords[1])])#  (min_x, min_y)
    
    return from_shape(box, srid= 4326)

def extract_gpx_data(trip_id:str, content: bytes):
    try:
        # Get route coordinates
        coords = []
        gpx = gpxpy.parse(content) 
        
        if not gpx.tracks:
            raise InvalidGPXError("GPX file contains no tracks")
        if len(gpx.tracks) > 1:
            raise InvalidGPXError("GPX file contains multiple tracks")
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
                    
        timestamp = gpx.tracks[0].segments[0].points[0].time
        
        if not timestamp:
            raise InvalidGPXError('GPX does not contain timestamps.')
            
        line = LineString(coords)
        linestring = from_shape(line, srid= 4326)
        
        # Get moving data
        moving_data = gpx.get_moving_data()
        distance = gpx.length_2d()
        ascent = gpx.get_uphill_downhill().uphill 
        high_point = gpx.get_elevation_extremes().maximum
        moving_time = moving_data.moving_time
        ride_date = timestamp.date()
        
        new_ride = Ride (
            trip_id = trip_id,
            notes = None,
            date = ride_date,
            distance = distance,
            elevation_gain = ascent,
            high_point = high_point,
            moving_time = moving_time,
            route = linestring,
            title = None,
        )
        return new_ride
        
    except InvalidGPXError as e:
        raise InvalidGPXError(f"Error creating ride: {e}")
    except Exception as e:
        raise InvalidGPXError(f"Error creating ride: {e}") from e

def validate_gpx_upload(file: UploadFile):
    
    if file.content_type not in ["multipart/form-data","application/gpx+xml", "application/xml", "text/xml", "application/octet-stream"] :
            raise InputError(f"Invalid content type header. Received: {file.content_type}")           
    if not file.filename.endswith('.gpx'):
            raise InputError(f'File : {file.filename} has Invalid file type. Supported types: .gpx')
    if file.size > config.limits.max_upload_size:
            raise InputError("Maximum file size exceeded. 15MB")
    if file.size == 0 :
            raise InputError(f"File : {file.filename} is empty")

    return True

@trip_router.get('/{trip_id}')
async def handler_get_trip(trip_id: str):
    trip = get_trip(trip_id)
    
    trip.route = to_geojson(to_shape(trip.route))
    trip.route = to_geojson(to_shape(trip.bounding_box))
    
    rides = get_trip_rides_asc(trip_id)
    
    for ride in rides:
        ride.route = to_geojson(to_shape(ride.route))
        
    return {'trip': trip, 'rides': rides}

@trip_router.get("/{trip_id}/rides")
async def handler_get_rides(trip_id:str) -> RideResponse | list[RideResponse]:
    
    rides = get_trip_rides_asc(trip_id)
    
    for ride in rides:
        ride.route = to_geojson(to_shape(ride.route))
        
    return rides
    
@trip_router.post('/')
async def handler_draft_trip(
    form_data: Annotated[TripDraft, Form()],
    auth_user: Annotated[User, Depends(get_auth_user)]) -> TripResponse:
    
    slug = generate_slug(form_data.title)
    
    new_trip = Trip(user_id = auth_user.id,
                    title = form_data.title,
                    description = form_data.description,
                    start_date = form_data.start_date,
                    end_date= form_data.end_date,
                    slug = slug
                    )
    
    return create_trip(new_trip)

@trip_router.post('/{trip_id}/upload')
async def handler_add_ride(
    trip_id: str, 
    file: UploadFile,
    auth_user: Annotated[User, Depends(get_auth_user)]
    ) -> RideResponse:
    
    trip = get_trip(trip_id)
    
    if auth_user.id != trip.user_id:
        raise UnauthorizedError("Error: Trip does not belong to user")
    
    validate_gpx_upload(file)
    
    content = await file.read()
    ride_data = extract_gpx_data(trip_id, content)
    
    ride = create_ride(ride_data)
    ride.route = to_geojson(to_shape(ride.route))
    return ride

@trip_router.post('/{trip_id}/upload/multi')
async def handler_add_rides(
    trip_id: str, 
    files: list[UploadFile],
    auth_user: Annotated[User, Depends(get_auth_user)]
    ) -> list[RideResponse]:
    
    trip = get_trip(trip_id)
    rides = []
    
    if len(files) > 15:
        raise InputError('Max number of files: 15')
    if auth_user.id != trip.user_id:
        raise UnauthorizedError("Error: Trip does not belong to user")
    
    for file in files:
        validate_gpx_upload(file)
    
    for file in files:
        content = await file.read()
        ride = extract_gpx_data(trip_id, content)
        rides.append(ride)
    
    rides = create_rides(rides)
    for ride in rides:
        ride.route = to_geojson(to_shape(ride.route))
        
    return rides

@trip_router.put('/{ride_id}')
async def handler_update_ride(
    ride_id: str, 
    form_data: Annotated[RideModel, Form()],
    auth_user: Annotated[User, Depends(get_auth_user)]
    ) -> RideResponse:
    
    trip = get_trip(get_ride(ride_id))
    if auth_user.id != trip.user_id:
        raise UnauthorizedError("Error: Ride does not belong to user")
    
    return update_ride(form_data.model_dump())

@trip_router.put('/{trip_id}/submit')
async def handler_save_trip(
    trip_id:str,
    form_data: Annotated[TripModel, Form()],
    auth_user: Annotated[User, Depends(get_auth_user)]):
    
    trip = get_trip(trip_id)
    
    if trip.user_id != auth_user.id:
        raise UnauthorizedError("Error: Trip does not belong to user")

    if form_data.end_date < form_data.start_date:
        raise InputError('End date cannot be before start date')
    
    values_dict = form_data.model_dump()
    
    route,total_distance,total_elevation,high_point = aggregate_trip(trip)
    
    values_dict['slug'] = generate_slug(form_data.title)
    values_dict['route'] = from_shape(route, srid= 4326)
    values_dict['total_distance'] = total_distance
    values_dict['total_elevation'] = total_elevation
    values_dict['high_point'] = high_point
    values_dict['bounding_box'] = generate_bounding_box(route)
    
    trip = update_trip(trip.id, values_dict)
    trip.bounding_box = to_geojson(to_shape(trip.bounding_box))
    trip.route = to_geojson(to_shape(trip.route))
    return trip

@trip_router.delete('/{trip_id}', status_code= 204)
async def handler_delete_trip(
    trip_id:str,
    auth_user: Annotated[User, Depends(get_auth_user)]):
    
    trip = get_trip(trip_id)
    if trip.user_id != auth_user.id:
        raise UnauthorizedError('Trip does not belong to user')
    
    delete_trip(trip_id)