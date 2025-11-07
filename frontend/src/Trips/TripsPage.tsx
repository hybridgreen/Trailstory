import { useEffect, useState } from "react";
import { getActiveUser, isAuthenticated, serverBaseURL } from "../utils";
import { useNavigate } from "react-router";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { LoginRedirect } from "@/Auth";
import { Spinner } from "@/components/ui/spinner";

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
    <div className="mb-8">
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
        <Button variant="outline" className="flex-1">
          <a href={`/trips/${trip.id}`}>View</a>
        </Button>
        <Button variant="default" className="flex-1">
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
    return <LoginRedirect />;
  }
  if (loading) {
    return (
      <div className="flex flex-auto justify-center items-center">
        <Spinner className="h-20 w-20" />
      </div>
    );
  }

  return (
    <div className="max-7xl mx-auto p-8">
      <NewTripButton />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {trips.length === 0 ? (
          <p>No trips yet. Create your first trip!</p>
        ) : (
          trips.map((trip) => <TripCard key={trip.id} trip={trip} />)
        )}
      </div>
    </div>
  );
}
