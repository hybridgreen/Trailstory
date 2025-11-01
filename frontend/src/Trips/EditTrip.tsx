import { useState, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Item, ItemContent, ItemMedia, ItemTitle } from "@/components/ui/item";
import { ChevronDown, ChevronRight, Trash2, Save } from "lucide-react";
import { toast } from "sonner";
import { Spinner } from "@/components/ui/spinner";

import { isTokenExpiring, refreshTokens, serverBaseURL } from "../utils";

export interface tripData {
  id: string;
  user_id: string;
  title: string;
  description: string;
  start_date: string;
  end_date: string | null;
  total_distance: number | null;
  total_elevation: number | null;
  high_point: number | null;
  route: string | null;
  bounding_box: string | null;
  slug: string | null;
  is_published: boolean;
}

export interface rideData {
  id: string;
  trip_id: string;
  title: string | null;
  notes: string | null;
  date: string;
  distance: number;
  elevation_gain: number;
  high_point: number;
  moving_time: number;
  gpx_url: string | null;
  route: string;
}

interface tripResponse {
  trip: tripData;
  rides: rideData[] | null;
}

function TripInfo({
  trip,
  onSave,
}: {
  trip: tripData;
  onSave: (getData: () => FormData) => void;
}) {
  const [isExpanded, setIsExpanded] = useState(true);
  const formRef = useRef<HTMLFormElement>(null);

  function getFormData() {
    return new FormData(formRef.current!);
  }

  useEffect(() => {
    onSave(getFormData);
  }, []);

  return (
    <Card className="mb-6">
      <CardHeader
        className="cursor-pointer hover:bg-gray-50"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <CardTitle>Trip Info</CardTitle>
          {isExpanded ? (
            <ChevronDown className="h-5 w-5" />
          ) : (
            <ChevronRight className="h-5 w-5" />
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <form
          ref={formRef}
          onSubmit={(e) => e.preventDefault()}
          className="space-y-2"
        >
          {isExpanded && (
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  name="title"
                  defaultValue={trip.title}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  name="description"
                  rows={4}
                  defaultValue={trip.description}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="start_date">Start Date</Label>
                <Input
                  id="start_date"
                  type="date"
                  name="start_date"
                  defaultValue={trip.start_date}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end_date">End Date</Label>
                <Input
                  id="end_date"
                  type="date"
                  name="end_date"
                  defaultValue={trip.end_date || trip.start_date}
                  required
                />
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="is_published" name="is_published" value="true" />
                <Label htmlFor="is_published" className="cursor-pointer">
                  Publish trip
                </Label>
              </div>
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  );
}

function UploadRidesInput(props: { onUpload: (files: FileList) => void }) {
  const [isExpanded, setIsExpanded] = useState(false);

  function handleFileSelect(event: React.ChangeEvent<HTMLInputElement>) {
    const files = event.target.files;

    if (!files || files.length === 0) {
      return;
    }
    props.onUpload(files);
    toast.success(`Uploading ${files.length} file(s)...`);
  }
  return (
    <Card className="mb-6">
      <CardHeader
        className="cursor-pointer hover:bg-gray-50"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Upload Rides</CardTitle>
            <CardDescription>Add GPX files to your trip</CardDescription>
          </div>
          {isExpanded ? (
            <ChevronDown className="h-5 w-5" />
          ) : (
            <ChevronRight className="h-5 w-5" />
          )}
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="gpxfiles">Select GPX Files</Label>
            <Input
              id="gpxfiles"
              type="file"
              name="gpxfiles"
              multiple
              accept=".gpx"
              onChange={handleFileSelect}
              className="cursor-pointer"
            />{" "}
          </div>
          <p className="text-sm text-muted-foreground">
            Upload up to 15 GPX files, 15MB or smaller each. Having issues?
            Contact support.
          </p>
        </CardContent>
      )}
    </Card>
  );
}

function RideCard({
  ride,
  onDelete,
  onSave,
}: {
  ride: rideData;
  onDelete: (id: string) => void;
  onSave: (rideID: string, getData: () => FormData) => void;
}) {
  const [isExpanded, setIsExpanded] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);

  async function handleDelete() {
    if (isTokenExpiring()) {
      await refreshTokens();
    }

    if (window.confirm(`Delete ride from ${ride.date}?`)) {
      if (isTokenExpiring()) {
        await refreshTokens();
      }
      const response = await fetch(`${serverBaseURL}/rides/${ride.id}/`, {
        method: "DELETE",
        headers: {
          authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (response.ok) {
        onDelete(ride.id);
        toast.success("Ride deleted");
      } else {
        alert("Failed to delete ride");
        toast.error("Failed to delete ride");
      }
    }
  }

  function getFormData() {
    return new FormData(formRef.current!);
  }

  useEffect(() => {
    onSave(ride.id, getFormData);
  }, []);

  function formatTime(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  }

  return (
    <Card className="mb-4">
      <CardHeader
        className="cursor-pointer hover:bg-gray-50"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg">
              {ride.title || `Ride on ${ride.date}`}
            </CardTitle>
            <CardDescription>
              {(ride.distance / 1000).toFixed(1)} km •{" "}
              {ride.elevation_gain.toFixed(0)} m gain
            </CardDescription>
          </div>
          {isExpanded ? (
            <ChevronDown className="h-5 w-5" />
          ) : (
            <ChevronRight className="h-5 w-5" />
          )}
        </div>
      </CardHeader>

      <form ref={formRef} onSubmit={(e) => e.preventDefault()}>
        <CardContent
          className="space-y-6"
          style={{ display: isExpanded ? "block" : "none" }}
        >
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor={`title-${ride.id}`}>Title</Label>
              <Input
                id={`title-${ride.id}`}
                name="title"
                defaultValue={ride.title || ""}
                placeholder="Name this ride"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor={`notes-${ride.id}`}>Notes</Label>
              <Textarea
                id={`notes-${ride.id}`}
                name="notes"
                rows={3}
                defaultValue={ride.notes || ""}
                placeholder="Add notes about this ride..."
              />
            </div>
          </div>

          <Separator />

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div>
              <Label className="text-muted-foreground text-sm">Date</Label>
              <p className="font-medium">{ride.date}</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-sm">Distance</Label>
              <p className="font-medium">
                {(ride.distance / 1000).toFixed(2)} km
              </p>
            </div>
            <div>
              <Label className="text-muted-foreground text-sm">Elevation</Label>
              <p className="font-medium">{ride.elevation_gain.toFixed(0)} m</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-sm">
                High Point
              </Label>
              <p className="font-medium">{ride.high_point.toFixed(0)} m</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-sm">
                Moving Time
              </Label>
              <p className="font-medium">{formatTime(ride.moving_time)}</p>
            </div>
          </div>

          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive" size="sm">
                <Trash2 className="h-4 w-4 mr-2" />
                Delete Ride
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete this ride?</AlertDialogTitle>
                <AlertDialogDescription>
                  This action cannot be undone. This will permanently delete the
                  ride from {ride.date}.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleDelete}>
                  Delete
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </CardContent>
      </form>
    </Card>
  );
}

export default function EditTripPage() {
  //Future fix - Uploading twice, refreshes the ride cards without previous upload

  const [tripData, setTripData] = useState<tripData | null>(null);
  const [rides, setRides] = useState<rideData[] | null>(null);
  const [loading, setLoading] = useState(true);
  const { id } = useParams();
  const navigate = useNavigate();
  const rideDataGetters = useRef<Map<string, () => FormData>>(new Map());
  const tripDataGetter = useRef<(() => FormData) | null>(null);

  useEffect(() => {
    async function fetchTrip() {
      if (isTokenExpiring()) {
        await refreshTokens();
      }
      try {
        const response = await fetch(`${serverBaseURL}/trips/${id}/`, {
          method: "GET",
        });

        if (response.ok) {
          const data: tripResponse = await response.json();
          setRides(data.rides);
          setTripData(data.trip);
        } else {
          const error = await response.json();
          console.error("Error:", error);
          toast.error("Failed to fetch trip");
        }
      } catch (error) {
        console.error("Unknown error:", error);
        toast.error("Network error");
      } finally {
        setLoading(false);
      }
    }
    fetchTrip();
  }, [id]);

  async function uploadRides(files: FileList) {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }
    try {
      if (isTokenExpiring()) {
        await refreshTokens();
      }
      const response = await fetch(`${serverBaseURL}/trips/${id}/rides/`, {
        method: "POST",
        headers: {
          authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: formData,
      });
      if (response.ok) {
        const data: rideData[] = await response.json();
        setRides(data);
        toast.success(`${data.length} ride(s) uploaded successfully!`);
      } else {
        const error = await response.json();
        console.error("Error:", error);
        toast.error(
          "Failed to upload rides: " + (error.detail || "Unknown error")
        );
      }
    } catch (error) {
      console.error("Unknown error:", error);
      toast.error("Network error");
    }
  }

  function handleDeleteRide(rideId: string) {
    setRides(rides?.filter((ride) => ride.id !== rideId) || null);
  }

  function registerRideData(rideId: string, getData: () => FormData) {
    rideDataGetters.current.set(rideId, getData);
  }

  function registerTripData(getData: () => FormData) {
    tripDataGetter.current = getData;
  }

  async function handleSaveAllRides() {
    if (isTokenExpiring()) {
      await refreshTokens();
    }
    let successCount = 0;

    for (const [rideId, getData] of rideDataGetters.current) {
      const formData = getData();

      try {
        const response = await fetch(`${serverBaseURL}/rides/${rideId}/`, {
          method: "PUT",
          headers: {
            authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: formData,
        });

        if (response.ok) {
          successCount++;
        }

        if (!response.ok) {
          console.error(`Failed to save ride ${rideId}`);
          console.log("Sent Data:");
          for (const [key, value] of formData.entries()) {
            console.log(key, value);
          }
        }
      } catch (error) {
        console.error(`Error saving ride ${rideId}:`, error);
      }
    }
    if (successCount > 0) {
      toast.success(`${successCount} ride(s) saved`);
    }
  }

  async function handleSaveTrip(tripID: string) {
    if (isTokenExpiring()) {
      await refreshTokens();
    }
    if (!tripDataGetter.current) {
      return;
    }

    const formData = tripDataGetter.current();

    try {
      const response = await fetch(`${serverBaseURL}/trips/${tripID}/`, {
        method: "PUT",
        headers: {
          authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: formData,
      });

      if (!response.ok) {
        toast.error("Failed to save trip");
        console.error(`Failed to save trip ${tripID}`);
        console.log("Sent Data:");
        for (const [key, value] of formData.entries()) {
          console.log(key, value);
        }
      }
      const trip: tripData = await response.json();
      toast.success("Trip saved successfully!");
      return trip;
    } catch (error) {
      toast.error("Network error");
    }
  }

  async function handleDeleteTrip() {
    if (isTokenExpiring()) {
      await refreshTokens();
    }

    if (window.confirm(`Delete trip?`)) {
      if (isTokenExpiring()) {
        await refreshTokens();
      }
      const response = await fetch(`${serverBaseURL}/trips/${tripData!.id}/`, {
        method: "DELETE",
        headers: {
          authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (response.ok) {
        toast.success("Trip deleted");
        navigate("/trips");
      } else {
        toast.error("Failed to delete trip");
      }
    }
  }

  async function handleSubmitTrip() {
    handleSaveAllRides();
    handleSaveTrip(tripData!.id);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Item variant="muted">
          <ItemMedia>
            <Spinner />
          </ItemMedia>
          <ItemContent>
            <ItemTitle className="line-clamp-1">Loading trip...</ItemTitle>
          </ItemContent>
        </Item>
      </div>
    );
  }

  if (!tripData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Item variant="muted">
          <ItemContent>
            <ItemTitle className="line-clamp-1">Trip not found</ItemTitle>
          </ItemContent>
        </Item>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Edit Trip</h1>
        <p className="text-muted-foreground">
          Manage your trip details and rides
        </p>
      </div>
      <TripInfo trip={tripData} onSave={registerTripData} />
      <UploadRidesInput onUpload={uploadRides} />

      {rides && rides.length > 0 && (
        <div className="mb-6">
          <h2 className="text-2xl font-semibold mb-4">
            Rides ({rides.length})
          </h2>
          {rides.map((ride) => (
            <RideCard
              key={ride.id}
              ride={ride}
              onDelete={handleDeleteRide}
              onSave={registerRideData}
            />
          ))}
        </div>
      )}
      <Separator />

      <div className="flex gap-4 justify-end bottom-6 bg-white p-4 border-t">
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button variant="destructive">
              <Trash2 className="h-4 w-4 mr-2" />
              Delete Trip
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete this trip?</AlertDialogTitle>
              <AlertDialogDescription>
                This action cannot be undone. This will permanently delete your
                trip and all associated rides.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleDeleteTrip}>
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        <Button onClick={handleSubmitTrip} size="lg">
          <Save className="h-4 w-4 mr-2" />
          Save Trip
        </Button>
      </div>
    </div>
  );
}
