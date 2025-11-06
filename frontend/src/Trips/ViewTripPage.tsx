import { useState, useEffect, useRef } from "react";
import { useParams } from "react-router";
import mapboxgl from "mapbox-gl";
import { serverBaseURL } from "../utils";
import "./ViewTripPage.css";
import type { tripData, rideData } from "./EditTrip";
import { Card, CardContent } from "@/components/ui/card";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN;

function PhotosCarousel({ links }: { links: string[] }) {
  return (
    <Carousel className="w-full max-w-4xl mx-auto">
      <CarouselContent>
        {links.map((link, index) => (
          <CarouselItem key={index}>
            <div className="p-1">
              <Card className="border-0 shadow-none">
                <CardContent className="p-0">
                  <img
                    src={link}
                    alt={`Photo ${index + 1}`}
                    className="w-full h-[500px] object-cover rounded-lg"
                  />
                </CardContent>
              </Card>
            </div>
          </CarouselItem>
        ))}
      </CarouselContent>
      <CarouselPrevious className="left-4" />
      <CarouselNext className="right-4" />
    </Carousel>
  );
}

export default function ViewTripPage() {
  const [trip, setTrip] = useState<tripData | null>(null);
  const [rides, setRides] = useState<rideData[]>([]);
  const [photos, setPhotos] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const { id } = useParams();
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    async function fetchTripData() {
      try {
        const tripResponse = await fetch(`${serverBaseURL}/trips/${id}/`);
        const tripData = await tripResponse.json();

        setTrip(tripData.trip);
        setRides(tripData.rides);
      } catch (error) {
        console.error("Error fetching trip:", error);
        alert("Failed to load trip");
      } finally {
        setLoading(false);
      }
    }

    fetchTripData();
  }, [id]);

  useEffect(() => {
    async function fetchTripPhotos() {
      setLoading(true);
      try {
        const response = await fetch(`${serverBaseURL}/trips/${id}/photos/`);
        const url_array = await response.json();
        console.log("Received:", url_array);
        setPhotos(url_array);
      } catch (error) {
        console.error("Error fetching trip:", error);
        alert("Failed to load trip");
      } finally {
        setLoading(false);
      }
    }
    fetchTripPhotos();
  }, [id]);

  useEffect(() => {
    if (!mapContainer.current || !trip || map.current) return;

    console.log("Initializing map...");

    const routeGeoJSON = JSON.parse(trip.route as string);
    const boundingBox = JSON.parse(trip.bounding_box as string);

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: "mapbox://styles/mapbox/outdoors-v12",
      center: [139.65, 35.68],
      zoom: 12,
    });

    map.current.on("load", () => {
      console.log("Map loaded!");

      map.current!.addSource("trip-route", {
        type: "geojson",
        data: {
          type: "Feature",
          properties: {},
          geometry: routeGeoJSON,
        },
      });

      map.current!.addLayer({
        id: "trip-route",
        type: "line",
        source: "trip-route",
        layout: {
          "line-join": "round",
          "line-cap": "round",
        },
        paint: {
          "line-color": "#e07a3f",
          "line-width": 3,
        },
      });

      // Fit map to bounding box
      // boundingBox.coordinates[0] is the polygon ring
      const coords = boundingBox.coordinates[0];
      const bounds = new mapboxgl.LngLatBounds(
        [coords[0][0], coords[0][1]], // Southwest corner
        [coords[2][0], coords[2][1]] // Northeast corner
      );

      map.current!.fitBounds(bounds, {
        padding: 50,
      });
    });

    // Cleanup
    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, [trip]);

  if (loading) {
    return <div className="trip-view-page">Loading trip...</div>;
  }

  if (!trip) {
    return <div className="trip-view-page">Trip not found</div>;
  }
  return (
    <div className="trip-view-page">
      <div className="trip-hero">
        <h1>{trip.title}</h1>

        <div className="trip-stats">
          <div className="stat">
            <span className="stat-value">
              {trip.total_distance
                ? (trip.total_distance / 1000).toFixed(1)
                : "0"}
            </span>
            <span className="stat-label">km</span>
          </div>
          <div className="stat">
            <span className="stat-value">
              {trip.total_elevation ? trip.total_elevation.toFixed(0) : "0"}
            </span>
            <span className="stat-label">m elevation</span>
          </div>
          <div className="stat">
            <span className="stat-value">
              {trip.high_point ? trip.high_point.toFixed(0) : "0"}
            </span>
            <span className="stat-label">m high point</span>
          </div>
          <div className="stat">
            <span className="stat-value">{rides.length}</span>
            <span className="stat-label">days</span>
          </div>
        </div>

        <p className="trip-description">{trip.description}</p>

        {/* Placeholder for photos */}
        <div>
          {photos.length > 0 ? (
            <PhotosCarousel links={photos} />
          ) : (
            <p>📷You have not added any pictures to your trip. Add some now!</p>
          )}
        </div>
      </div>

      {/* Map */}
      <div className="map-section">
        <h2>Route</h2>
        <div ref={mapContainer} className="map-container" />
      </div>
    </div>
  );
}
