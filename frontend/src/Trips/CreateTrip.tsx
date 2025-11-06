import { useNavigate } from "react-router";
import { isTokenExpiring, refreshTokens, serverBaseURL } from "../utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function DraftTripForm() {
  const navigate = useNavigate();

  async function draftTrip(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    if (formData.get("end_date") === "") {
      formData.delete("end_date");
    }
    try {
      if (isTokenExpiring()) {
        await refreshTokens();
      }
      const response = await fetch(`${serverBaseURL}/trips/`, {
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
    <div className="container max-w-2xl mx-auto py-8">
      <Card>
        <CardHeader>
          <CardTitle>Create New Trip</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={draftTrip} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="title">Title</Label>
              <Input type="text" id="title" name="title" required />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea id="description" name="description" rows={4} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="start_date">Start Date</Label>
              <Input type="date" id="start_date" name="start_date" required />
            </div>

            <div className="space-y-2">
              <Label htmlFor="end_date">End Date (optional)</Label>
              <Input type="date" id="end_date" name="end_date" />
            </div>

            <Button type="submit" className="w-full">
              Create Draft
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
