import { serverBaseURL } from "./App";
import { useNavigate } from "react-router";

export default function DraftTripForm() {
  const navigate = useNavigate();

  async function draftTrip(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    if (formData.get("end_date") === "") {
      formData.delete("end_date");
    }
    try {
      const response = await fetch(`${serverBaseURL}trips`, {
        method: "POST",
        headers: {
          authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: formData,
      });

      if (response.ok) {
        const tripDraft = await response.json();
        console.log("Created trip", tripDraft);
        navigate(`/trips/${tripDraft.id}/edit`);
      } else {
        const error = await response.json();
        console.error("Error:", error);
        alert("Failed to create trip: " + (error.detail || "Unknown error"));
      }
    } catch (error) {
      console.error("Unknown error:", error);
    }
  }

  return (
    <div className="trip-page">
      <form onSubmit={draftTrip}>
        <div className="trip-info-section">
          <h3>Create New Trip</h3>
          <div className="trip-info-form">
            <div>
              <label>Title</label>
              <input type="text" name="title" required />
            </div>
            <div>
              <label>Description</label>
              <textarea name="description" rows={4} />
            </div>
            <div>
              <label>Start Date</label>
              <input type="date" name="start_date" required />
            </div>
            <div>
              <label>End Date (optional)</label>
              <input type="date" name="end_date" />
            </div>
          </div>
        </div>
        <div>
          <button type="submit">Create Draft</button>
        </div>
      </form>
    </div>
  );
}
