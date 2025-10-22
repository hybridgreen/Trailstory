from fastapi.exceptions import ValidationException
from fastapi.testclient import TestClient
from app.main import app
import pytest
from app.errors import *
from app.config import config
from pathlib import Path


client = TestClient(app)

def reset():
    client.post(
        '/admin/reset',
        headers= {"Authorization": f"Bearer {config.auth.admin_token}"})

@pytest.fixture(scope='function')
def setup():
    
    reset()
    
    test_user = {
        "email": "samle@pineapple.com",
        "username": "spongebob",
        "password": "YourNameIs123!"
    }
    user = client.post('/users', data = test_user)
    user_response =  user.json()
    
    at = user_response['access_token']
    
    test_trip = { 
                    'title': 'The Lanna Kingdom',
                    'description': "390km in Thailand.",
                    'start_date': '2025-12-01'            
                }

    trip = client.post(
            '/trips',
            data= test_trip,
            headers= {"Authorization": f"Bearer {at}"}
        )
    
    trip_data = trip.json()
    trip_id = trip_data['id']

    tests_dir = Path(__file__).parent.parent 
    samples_dir =tests_dir.joinpath('../samples')

    ride1_path = samples_dir.joinpath('ride1.gpx')
    ride2_path = samples_dir.joinpath('ride2.gpx')
    ride3_path = samples_dir.joinpath('ride3.gpx')
    
    f1 = open(ride1_path, 'rb')
    f2 = open(ride2_path, 'rb')
    f3 = open(ride3_path, 'rb')

    response = client.post(
        f'/trips/{trip_id}/upload/multi',
        files=[
            ('files', ('ride1.gpx', f1, "application/gpx+xml")),
            ('files', ('ride2.gpx', f2, "application/gpx+xml")),
            ('files', ('ride3.gpx', f3, "application/gpx+xml"))
        ],
        headers={"Authorization": f"Bearer {at}"}
    )

    f1.close()
    f2.close()
    f3.close()
        
    return user_response, trip_data

def test_retrieve_user(setup):
    
    user_response, trip_data = setup
    at = user_response['access_token']
    user_data = user_response['user']
    
    fetched = client.get(
        '/users/me',
        headers= {"Authorization": f"Bearer {at}"}
    )
    
    data = fetched.json()
    
    assert fetched.status_code == 200
    assert data['id'] == user_data['id']

def test_update_user(setup):
    
    user_response, trip_data = setup
    at = user_response['access_token']
    user_data = user_response['user']
    
    update = {
        'firstname': 'Robert',
        'lastname': 'Spongey'
    }
    
    fetched = client.put(
        '/users',
        data= update,
        headers= {"Authorization": f"Bearer {at}"}
    )
    
    data = fetched.json()
    
    assert fetched.status_code == 200
    assert data['id'] == user_data['id']
    assert data['firstname'] == 'Robert'
    assert data['lastname'] == 'Spongey'

def test_retrieve_trip(setup):
    
    user_response, trip_data = setup
    at = user_response['access_token']
    user_data = user_response['user']
    user_id = user_data['id']
    
    fetched = client.get(f'/users/{user_id}/trips')
    trips = fetched.json()
    
    for trip in trips:
        assert trip['title'] == trip_data['title']
        assert trip['id'] == trip_data['id']

def test_delete_user(setup):

    user_response, trip_data = setup
    at = user_response['access_token']
    user_data = user_response['user']
    user_id = user_data['id']
    
    fetched = client.get(f'/users/{user_id}/trips')
    trip = fetched.json()[0]
    
    assert trip['id'] != ''
    
    response = client.delete(
        '/users/',
        headers={"Authorization": f"Bearer {at}"}
        )
    
    assert response.status_code == 204
    
    #Checking if trips deleted in cascasde
    fetched = client.get(f'/users/{user_id}/trips')
    trip = fetched.json()
    
    assert fetched.status_code == 200
    assert len(trip) == 0
    

