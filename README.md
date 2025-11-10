# Trailstory

**Create beautiful pages for your adventures**

<img src="https://github.com/hybridgreen/Trailstory/blob/082ce18d3cfe8f25e7522e100e6a5c707f37b2b3/static/TripPage" alt="Trailstory Trip page" width="60%"/>

Combine your multi-day aventure into a shareable page. Revisit your personal notes, photos, gear loadout and routes in one place. Get a day by day breakdown of your trip at the end. 

Try it for yourself: 	[Trailstory]([https://www.example.com](https://trailstory.vercel.app/dashboard))

Built with FastAPI, React, Postgres+PostGIS 

## Technical Implementation

PostGIS geometry types for route data & spatial queries
Custom route aggregation logic for multi-day trip processing
Custom authentication system (JWT tokens, rotating tokens, one-time tokens)
Relational schema for domain entities: Users, Trips, Rides, Photos

## Architecture
<img src="https://github.com/hybridgreen/Trailstory/blob/39e8f11285c89f3c2aee7a70e491656c3b441a0f/static/archV0.svg" alt="Architecture" width="100%"/>
Frontend: React
Backend: FastAPI 
Auth: Custom JWT + bcrypt
Database: PostgreSQL + PostGIS → ORM: SQLAlchemy 2.0 + GeoAlchemy2   
File Storage: S3   
Image Processing: Pillow   
GPX Processing: gpxpy 1.6.2   

Why PostGIS over storing JSON?
How trip aggregation works
Database schema design
Why certain trade-offs

Key Features
Architecture
Quick Start/Installation
Roadmap (optional)

