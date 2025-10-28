import { useEffect, useState } from "react";
import { getActiveUser } from "./Auth";

const baseURL = "http://127.0.0.1:8000/";

interface tripData {
  id: string;
  user_id: string;
  title: string;
  description: string;
  start_date: number | null;
  slug: string | null;
  is_published: boolean;
}

interface userResponse {
  id: string;
  email: string;
  username: string;
  firstname: string | null;
  lastname: string | null;
  email_verified: boolean;
  created_at: number;
}

async function fetchUserTrips(userID: string): Promise<tripData[]> {
  try {
    const response = await fetch(`${baseURL}users/${userID}/trips`, {
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

async function fetchUser(userID: string): Promise<userResponse | null> {
  try {
    const response = await fetch(`${baseURL}users/${userID}`, {
      method: "GET",
    });
    if (response.ok) {
      const user = await response.json();
      console.log("Fetched user", user);
      return user;
    } else {
      const error = await response.json();
      console.error("Error:", error);
      return null;
    }
  } catch (error) {
    console.error("Unknown error:", error);
    return null;
  }
}

function NewTripButton() {
  return (
    <div className="add-trip-button">
      <button>New Trip</button>
    </div>
  );
}

function TripCard({ trip }: { trip: tripData }) {
  return (
    <div className="trip-card">
      <a href={`${baseURL}${trip.user_id}/${trip.slug}`}>
        <div>
          <img
            src="https://placehold.co/300x200/3d4f2f/faf8f3?text=Bikepacking+Trip"
            alt="Trip thumbnail"
          />
        </div>
        <div>
          <h3>{trip.title}</h3>
        </div>
      </a>
    </div>
  );
}

export default function Dashboard() {
  const [trips, setTrips] = useState<tripData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTrips() {
      const user = getActiveUser();
      console.log("Active user:", user.username);
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
    <div className="dashboard">
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
