import { serverBaseURL } from "./App";
import { useState, useEffect } from "react";
import { useParams } from "react-router";
import "./EditTrip.css";

interface tripData {
  id: string;
  user_id: string;
  title: string;
  description: string;
  start_date: string | null;
  end_date: string | null;
  total_distance: number | null;
  total_elevation: number | null;
  high_point: number | null;
  route: string | null;
  bounding_box: string | null;
  slug: string | null;
  is_published: boolean;
}

interface TripInfoProps {
  data: tripData;
}

function TripInfo({ data }: TripInfoProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="trip-info-section">
      <div
        className="section-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <h3>Trip Info</h3>
        <button type="button">{isExpanded ? "▼" : "▶"}</button>
      </div>

      {isExpanded && (
        <div className="trip-info-form">
          <div>
            <label>Title</label>
            <input
              type="text"
              name="title"
              defaultValue={data.title}
              required
            />
          </div>
          <div>
            <label>Description</label>
            <textarea
              name="description"
              rows={4}
              defaultValue={data.description}
            />
          </div>
          <div>
            <label>Start Date</label>
            <input
              type="date"
              name="start_date"
              defaultValue={data.start_date || ""}
              required
            />
          </div>
          <div>
            <label>End Date (optional)</label>
            <input
              type="date"
              name="end_date"
              defaultValue={data.end_date || ""}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function RideCard() {
  return <div></div>;
}

export default function EditTripPage() {
  const [step, setStep] = useState("draft"); // 'draft', 'upload', 'rides'
  const [tripData, setTripData] = useState<tripData | null>(null);
  const [rides, setRides] = useState([]);
  const [loading, setLoading] = useState(true);
  const { id } = useParams();

  useEffect(() => {
    async function fetchTrip() {
      try {
        const response = await fetch(`${serverBaseURL}trips/${id}`, {
          method: "GET",
        });

        if (response.ok) {
          const data = await response.json();
          setTripData(data);
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

  if (loading) {
    return <div>Loading trip...</div>;
  }

  if (!tripData) {
    return <div>Trip not found</div>;
  }

  return (
    <div className="trip-page">
      <TripInfo data={tripData} />
      <div>
        <button type="submit">Save Draft</button>
      </div>
    </div>
  );
}
