import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { isTokenExpiring, refreshTokens, serverBaseURL } from "./utils";
import "./Profile.css";

interface UserProfile {
  id: string;
  email: string;
  username: string;
  firstname: string | null;
  lastname: string | null;
  email_verified: boolean;
  created_at: string;
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchProfile() {
      if (isTokenExpiring()) {
        await refreshTokens();
      }

      try {
        const response = await fetch(`${serverBaseURL}/users/me/`, {
          method: "GET",
          headers: {
            authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setProfile(data);
        } else {
          const error = await response.json();
          console.error("Error:", error);
          alert("Failed to load profile");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("Network error");
      } finally {
        setLoading(false);
      }
    }
    fetchProfile();
  }, []);

  async function handleSaveProfile(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (isTokenExpiring()) {
      await refreshTokens();
    }

    const formData = new FormData(event.currentTarget);

    try {
      const response = await fetch(`${serverBaseURL}/users/`, {
        method: "PUT",
        headers: {
          authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: formData,
      });

      if (response.ok) {
        const updatedProfile = await response.json();
        setProfile(updatedProfile);
        setIsEditing(false);
        alert("Profile updated!");
      } else {
        const error = await response.json();
        console.error("Error:", error);
        alert("Failed to update profile");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Network error");
    }
  }

  if (loading) {
    return <div className="profile-page">Loading profile...</div>;
  }

  if (!profile) {
    return <div className="profile-page">Profile not found</div>;
  }

  function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  }

  return (
    <div className="profile-page">
      <div className="profile-card">
        <h2>My Profile</h2>

        {isEditing ? (
          <form onSubmit={handleSaveProfile}>
            <div className="profile-section">
              <div className="profile-field">
                <label>First name</label>
                <input
                  type="text"
                  name="firstname"
                  defaultValue={profile.firstname || ""}
                  placeholder="Enter first name"
                />
              </div>
              <div className="profile-field">
                <label>Last name</label>
                <input
                  type="text"
                  name="lastname"
                  defaultValue={profile.lastname || ""}
                  placeholder="Enter last name"
                />
              </div>
              <div className="profile-field">
                <label>Username</label>
                <input
                  type="text"
                  name="username"
                  defaultValue={profile.username}
                  required
                />
              </div>
              <div className="profile-field">
                <label>Email</label>
                <span>
                  {profile.email}
                  {profile.email_verified ? (
                    <span className="verified-badge">✓ Verified</span>
                  ) : (
                    <button className="unverified-badge">
                      Verify your email
                    </button>
                  )}
                </span>
              </div>
              <div className="profile-field">
                <label>Member Since</label>
                <span>{formatDate(profile.created_at)}</span>
              </div>
            </div>

            <div className="profile-actions">
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="cancel-btn"
              >
                Cancel
              </button>
              <button type="submit">Save Changes</button>
            </div>
          </form>
        ) : (
          <>
            <div className="profile-section">
              <div className="profile-field">
                <label>First name</label>
                <span>{profile.firstname || "Not set"}</span>
              </div>
              <div className="profile-field">
                <label>Last name</label>
                <span>{profile.lastname || "Not set"}</span>
              </div>
              <div className="profile-field">
                <label>Username</label>
                <span>{profile.username}</span>
              </div>
              <div className="profile-field">
                <label>Email</label>
                <span>
                  {profile.email}
                  {profile.email_verified ? (
                    <span className="verified-badge">✓ Verified</span>
                  ) : (
                    <button className="unverified-badge">
                      Verify your email
                    </button>
                  )}
                </span>
              </div>

              <div className="profile-field">
                <label>Member Since</label>
                <span>{formatDate(profile.created_at)}</span>
              </div>
            </div>

            <div className="profile-actions">
              <button onClick={() => setIsEditing(true)}>Edit Profile</button>
              <button onClick={() => navigate("/trips")}>My Trips</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
