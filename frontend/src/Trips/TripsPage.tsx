import { useEffect, useState } from "react";
import {
  getActiveUser,
  isAuthenticated,
  clientBaseURL,
  serverBaseURL,
} from "../utils";
import { useNavigate } from "react-router";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar, MapPin, TrendingUp } from "lucide-react";
import "./tripspage.css";
import { Button } from "@/components/ui/button";

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
    const response = await fetch(`${serverBaseURL}/users/${userID}/trips/`, {
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
      <Button onClick={newTripHandler}>New Trip</Button>
    </div>
  );
}

function TripCard({ trip }: { trip: tripsData }) {
  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <a href={`/trips/${trip.id}`} className="block">
        <img
          src="https://placehold.co/400x250/3d4f2f/faf8f3?text=Bikepacking+Trip"
          alt={trip.title}
          className="w-full h-48 object-cover"
        />
      </a>

      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle className="text-xl">{trip.title}</CardTitle>
          {trip.is_published ? (
            <Badge variant="default">Published</Badge>
          ) : (
            <Badge variant="secondary">Draft</Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-2">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Calendar className="h-4 w-4" />
          <span>{trip.start_date}</span>
        </div>
      </CardContent>

      <CardFooter className="gap-2">
        <Button variant="outline" className="flex-1" asChild>
          <a href={`/trips/${trip.id}`}>View</a>
        </Button>
        <Button variant="default" className="flex-1" asChild>
          <a href={`/trips/${trip.id}/edit`}>Edit</a>
        </Button>
      </CardFooter>
    </Card>
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

  if (!isAuthenticated()) {
    return <div className="trips">Please login to see your trips.</div>;
  }
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
