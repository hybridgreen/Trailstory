# Trailstory - One app to track your stories
[![Tests](https://github.com/hybridgreen/Trailstory/actions/workflows/CI.yml/badge.svg)](https://github.com/hybridgreen/Trailstory/actions/workflows/CI.yml)

🚀 **Live at:** [Trailstory](https://trailstory.vercel.app) 

Full-stack adventure tracker deployed on GCP (API), Vercel (frontend), and Supabase (PostGIS database).

## Demo 

 **Try the live demo at:** [Trailstory](https://trailstory.vercel.app) 
 No signup required

<div align="center">
  <img src="/static/TripPage" alt="Trailstory Trip page" width="60%"/>
</div>

Combine your multi-day adventure into a shareable page. Revisit your personal notes, photos, gear loadout and routes in one place. Get a day by day breakdown of your trip at the end. 


## Key Features

- PostGIS geometry types for route data & spatial queries
- Custom route aggregation logic for multi-day trip processing
- Custom authentication system (JWT tokens, rotating tokens, one-time tokens)
- Relational schema for domain entities: Users, Trips, Rides, Photos

### Future Features

- Nearby trips: "Find trips within X km of this location"
- Photos near route: "Show photos taken along this route"
- Bounding box search: "Show trips in this map viewport"
- Strava / Garmin Webhook for trip syncing

## Architecture

<div align="center">
  <img src="static/archV0.svg" alt="Architecture" width="70%"/>
</div>

## Production Architecture

- **Frontend:** React + Shadcn UI
- **API:** Python/FastAPI 
- **Database:** PostgreSQL + PostGIS
- **Storage:** AWS S3 for image storage
- **Deployment:** Google Cloud Run

## Design Decisions

**Storing and Querying Geospacial data with PostGIS**

GPS routes need efficient storage and querying for aggregation and map rendering. Rather than storing GPX files as text or JSON arrays, I converted them to PostGIS LINESTRING geometry types.

The trade offs were added database complexity and requires PostGIS extension, but enables:
- Spatial queries (bounding box calculation, point-in-route checks)
- Native geometry operations (route merging, simplification)
- Future features (nearby ride discovery, route similarity)

  
**Trip aggregation**

Users upload individual GPX files for each day's ride. Each ride's coordinates are parsed and stored as a PostGIS LINESTRING geometry in the database.
Aggregation process:
- Query retrieves all rides for a trip, ordered chronologically by date
- Extract coordinates from each ride's LINESTRING geometry
- Concatenate routes end-to-start into a single continuous LineString
- Calculate aggregate statistics (total distance, elevation gain, highest point)
- Generate bounding box encompassing all rides

Why this approach:

- Preserves individual ride data for day-by-day breakdown
- Enables both per-ride and full trip views
- Aggregation computed on-demand, not stored redundantly

**Authentication Strategy**

I decided to implement custom JWT access tokens, Rotating refresh tokens and one-time token workflows rather than use libraries to better understand security and token lifecycles. 

