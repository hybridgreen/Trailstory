import { useEffect, useState } from "react";
import { getActiveUser } from "./Auth";

import { clientBaseURL, serverBaseURL } from "./App";
import { useNavigate } from "react-router";

import "./tripspage.css";

interface tripsData {
  id: string;
  user_id: string;
  title: string;
  description: string;
  start_date: number | null;
  slug: string | null;
  is_published: boolean;
}

async function fetchUserTrips(userID: string): Promise<tripsData[]> {
  try {
    const response = await fetch(`${serverBaseURL}users/${userID}/trips`, {
      method: "GET",
      headers: {
        authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    });
    if (response.ok) {
      const trips = await response.json();
      console.log("Fetched trips", trips);
      return trips;
    } else {
      const error = await response.json();
      console.error("Error:", error);
      return [];
    }
  } catch (error) {
    console.error("Unknown error:", error);
    return [];
  }
}

function NewTripButton() {
  const navigate = useNavigate();

  function newTripHandler() {
    navigate("/trips/new");
  }
  return (
    <div className="add-trip-button">
      <button onClick={newTripHandler}>New Trip</button>
    </div>
  );
}

function TripCard({ trip }: { trip: tripsData }) {
  return (
    <div className="trip-card">
      <a href={`${serverBaseURL}${trip.user_id}/${trip.slug}`}>
        <div>
          <img
            src="https://placehold.co/300x200/3d4f2f/faf8f3?text=Bikepacking+Trip"
            alt="Trip thumbnail"
          />
        </div>
      </a>
      <a href={`${clientBaseURL}trips/${trip.id}/edit`}>
        <div>
          <h3>{trip.title}</h3>
        </div>
      </a>
    </div>
  );
}

export default function Trips() {
  const [trips, setTrips] = useState<tripsData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTrips() {
      const user = getActiveUser();
      const userTrips = await fetchUserTrips(user.id);
      setTrips(userTrips);
      setLoading(false);
    }
    loadTrips();
  }, []);

  if (loading) {
    return <div>Loading trips...</div>;
  }

  return (
    <div className="trips">
      <NewTripButton />
      <div className="trip-grid">
        {trips.length === 0 ? (
          <p>No trips yet. Create your first trip!</p>
        ) : (
          trips.map((trip) => <TripCard key={trip.id} trip={trip} />)
        )}
      </div>
    </div>
  );
}
