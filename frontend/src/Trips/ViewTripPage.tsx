import { useState, useEffect, useRef } from "react";
import { useParams } from "react-router";
import mapboxgl from "mapbox-gl";
import { serverBaseURL } from "../utils";
import type { tripData, rideData } from "./EditTrip";
import { Spinner } from "@/components/ui/spinner";
import PhotosCarousel from "@/components/PhotosCarousel";

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN;

export default function ViewTripPage() {
  const [trip, setTrip] = useState<tripData | null>(null);
  const [rides, setRides] = useState<rideData[]>([]);
  const [photos, setPhotos] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const { id } = useParams();
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    setLoading(true);
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
    return (
      <div className="flex flex-auto justify-center items-center">
        <Spinner className="h-20 w-20" />
      </div>
    );
  }

  if (!trip) {
    return <div className="trip-view-page">Trip not found</div>;
  }
  return (
    <div className="flex flex-col max-w-6xl mx-auto p-8">
      <div className="mb-12">
        <h1 className="text-5xl font-bold text-[#3d4f2f] mb-6">{trip.title}</h1>

        <div className="grid gap-8 grid-cols-2 md:grid-cols-4 m-8 p-8 bg-amber-50 rounded-lg">
          <div className="flex flex-col items-center">
            <span className="text-4xl font-bold text-[#e07a3f]">
              {trip.total_distance
                ? (trip.total_distance / 1000).toFixed(1)
                : "0"}
            </span>
            <span className="text-sm text-gray-600 uppercase tracking-wide">
              km
            </span>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-4xl font-bold text-[#e07a3f]">
              {trip.total_elevation ? trip.total_elevation.toFixed(0) : "0"}
            </span>
            <span className="text-sm text-gray-600 uppercase tracking-wide">
              m elevation
            </span>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-4xl font-bold text-[#e07a3f]">
              {trip.high_point ? trip.high_point.toFixed(0) : "0"}
            </span>
            <span className="text-sm text-gray-600 uppercase tracking-wide">
              m high point
            </span>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-4xl font-bold text-[#e07a3f]">
              {rides.length}
            </span>
            <span className="text-sm text-gray-600 uppercase tracking-wide">
              days
            </span>
          </div>
        </div>

        <p className="text-lg text-[#2c2c2c] leading-relaxed mx-8 mb-8">
          {trip.description}
        </p>

        <div className="bg-gray-100 p-8 rounded-lg">
          {photos.length > 0 ? (
            <PhotosCarousel links={photos} />
          ) : (
            <p className="text-center text-gray-600">
              📷 You have not added any pictures to your trip. Add some now!
            </p>
          )}
        </div>
      </div>

      <div className="mt-12">
        <h2 className="text-2xl font-semibold text-[#3d4f2f] mb-4">Routes</h2>
        <div
          ref={mapContainer}
          className="w-full h-[500px] rounded-lg overflow-hidden"
        />
      </div>
    </div>
  );
}
