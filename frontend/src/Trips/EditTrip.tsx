import { serverBaseURL } from "../App";
import { useState, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router";
import "./EditTrip.css";
import { isTokenExpiring, refreshTokens } from "../utils";

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
    <div className="trip-info-section">
      <div
        className="section-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <h3>Trip Info</h3>
        <button type="button">{isExpanded ? "▼" : "▶"}</button>
      </div>
      <form
        ref={formRef}
        onSubmit={(e) => e.preventDefault()}
        className="trip-info-form"
      >
        {isExpanded && (
          <div>
            <div>
              <label>Title</label>
              <input
                type="text"
                name="title"
                defaultValue={trip.title}
                required
              />
            </div>
            <div>
              <label>Description</label>
              <textarea
                name="description"
                rows={4}
                defaultValue={trip.description}
                required
              />
            </div>
            <div>
              <label>Start Date **</label>
              <input
                type="date"
                name="start_date"
                defaultValue={trip.start_date}
                required
              />
            </div>
            <div>
              <label>End Date **</label>
              <input
                type="date"
                name="end_date"
                defaultValue={trip.end_date || trip.start_date}
                required
              />
            </div>

            <span>
              <label>Publish?</label>
              <input type="checkbox" name="is_published" value={"true"} />
            </span>
          </div>
        )}
      </form>
    </div>
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
  }
  return (
    <div className="ride-upload-section">
      <div
        className="section-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <h3>Upload rides</h3>
        <button type="button">{isExpanded ? "▼" : "▶"}</button>
      </div>
      {isExpanded && (
        <div>
          <div>
            <label>Select your rides to upload</label>
          </div>
          <input
            type="file"
            name="gpxfiles"
            multiple
            onChange={handleFileSelect}
          />
          <h6>
            Works for multiple .gpx files 15MB or smaller. Choose up to 15
            files. If you have any problems uploading your files, contact
            support for help.
          </h6>
        </div>
      )}
    </div>
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
      const response = await fetch(`${serverBaseURL}/rides/${ride.id}`, {
        method: "DELETE",
        headers: {
          authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (response.ok) {
        onDelete(ride.id);
      } else {
        alert("Failed to delete ride");
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
    <div className="ride-card">
      <div
        className="section-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div>
          <h4>{ride.title || `Ride on ${ride.date}`}</h4>
          <span className="ride-stats-preview">
            {(ride.distance / 1000).toFixed(1)} km •{" "}
            {ride.elevation_gain.toFixed(0)} m gain
          </span>
        </div>
        <button type="button">{isExpanded ? "▼" : "▶"}</button>
      </div>
      <form
        ref={formRef}
        onSubmit={(e) => e.preventDefault()}
        className="ride-form"
      >
        <div
          className="ride-details"
          style={{ display: isExpanded ? "block" : "none" }}
        >
          <div>
            <label>Title</label>
            <input
              type="text"
              name="title"
              defaultValue={ride.title || ""}
              placeholder="Name this ride"
            />
          </div>
          <div>
            <label>Notes</label>
            <textarea
              name="notes"
              rows={3}
              defaultValue={ride.notes || ""}
              placeholder="Add notes about this ride..."
            />
          </div>

          <div className="ride-stats">
            <div className="stat">
              <label>Date</label>
              <span>{ride.date}</span>
            </div>
            <div className="stat">
              <label>Distance</label>
              <span>{(ride.distance / 1000).toFixed(2)} km</span>
            </div>
            <div className="stat">
              <label>Elevation Gain</label>
              <span>{ride.elevation_gain.toFixed(0)} m</span>
            </div>
            <div className="stat">
              <label>High Point</label>
              <span>{ride.high_point.toFixed(0)} m</span>
            </div>
            <div className="stat">
              <label>Moving Time</label>
              <span>{formatTime(ride.moving_time)}</span>
            </div>
          </div>

          <div className="ride-actions">
            <button type="button" onClick={handleDelete} className="delete-btn">
              Delete Ride
            </button>
          </div>
        </div>
      </form>
    </div>
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
        const response = await fetch(`${serverBaseURL}/trips/${id}`, {
          method: "GET",
        });

        if (response.ok) {
          const data: tripResponse = await response.json();
          setRides(data.rides);
          setTripData(data.trip);
        } else {
          const error = await response.json();
          console.error("Error:", error);
          alert("Failed to fetch trip: " + (error.detail || "Unknown error"));
        }
      } catch (error) {
        console.error("Unknown error:", error);
        alert("Network error");
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
      const response = await fetch(`${serverBaseURL}/trips/${id}/rides`, {
        method: "POST",
        headers: {
          authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: formData,
      });
      if (response.ok) {
        const data: rideData[] = await response.json();
        setRides(data);
      } else {
        const error = await response.json();
        console.error("Error:", error);
        alert("Failed to upload rides: " + (error.detail || "Unknown error"));
      }
    } catch (error) {
      console.error("Unknown error:", error);
      alert("Network error");
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

    for (const [rideId, getData] of rideDataGetters.current) {
      const formData = getData();

      try {
        const response = await fetch(`${serverBaseURL}/rides/${rideId}`, {
          method: "PUT",
          headers: {
            authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
          body: formData,
        });

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
      const response = await fetch(`${serverBaseURL}/trips/${tripID}`, {
        method: "PUT",
        headers: {
          authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: formData,
      });

      if (!response.ok) {
        console.error(`Failed to save trip ${tripID}`);
        console.log("Sent Data:");
        for (const [key, value] of formData.entries()) {
          console.log(key, value);
        }
      }
      const trip: tripData = await response.json();
      console.log("Saved trip:", trip.title);
      console.log(trip);
      console.log(trip.route);
      console.log(trip.bounding_box);
    } catch (error) {
      console.error(`Error saving trip ${tripID}:`, error);
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
      const response = await fetch(`${serverBaseURL}/trips/${tripData!.id}`, {
        method: "DELETE",
        headers: {
          authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (response.ok) {
        navigate("/trips");
      } else {
        alert("Failed to delete trip");
      }
    }
  }

  async function handleSubmitTrip() {
    handleSaveAllRides();
    handleSaveTrip(tripData!.id);
  }

  if (loading) {
    return <div>Loading trip...</div>;
  }

  if (!tripData) {
    return <div>Trip not found</div>;
  }

  return (
    <div className="trip-page">
      <TripInfo trip={tripData} onSave={registerTripData} />
      <UploadRidesInput onUpload={uploadRides} />

      {rides && rides.length > 0 && (
        <div className="rides-section">
          <h3>Rides ({rides.length})</h3>
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

      <div>
        <span>
          <button name="delete" onClick={handleDeleteTrip}>
            Delete Trip
          </button>
        </span>
        <span>
          <button type="submit" onClick={handleSubmitTrip}>
            Save Trip
          </button>
        </span>
      </div>
    </div>
  );
}
