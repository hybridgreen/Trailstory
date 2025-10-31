import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { isTokenExpiring, refreshTokens, serverBaseURL } from "./utils";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Calendar, Mail, User, CheckCircle, XCircle } from "lucide-react";
import { Progress } from "./components/ui/progress";

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
    return (
      <div className="profile-page">
        <Progress value={67} />
        Loading profile...
      </div>
    );
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
    <div className="max-w-2xl mx-auto p-6">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <Avatar className="h-20 w-20">
              <AvatarImage src="https://github.com/shadcn.png" />
              <AvatarFallback>
                {profile.firstname?.[0]}
                {profile.lastname?.[0]}
              </AvatarFallback>
            </Avatar>
            <div>
              <CardTitle className="text-2xl">
                {profile.firstname || profile.lastname
                  ? `${profile.firstname || ""} ${
                      profile.lastname || ""
                    }`.trim()
                  : profile.username}
              </CardTitle>
              <CardDescription>@{profile.username}</CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {isEditing ? (
            <form onSubmit={handleSaveProfile} className="space-y-6">
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="firstname">First Name</Label>
                    <Input
                      id="firstname"
                      name="firstname"
                      defaultValue={profile.firstname || ""}
                      placeholder="Enter first name"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastname">Last Name</Label>
                    <Input
                      id="lastname"
                      name="lastname"
                      defaultValue={profile.lastname || ""}
                      placeholder="Enter last name"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    name="username"
                    defaultValue={profile.username}
                    required
                  />
                </div>

                <Separator />

                <div className="space-y-2">
                  <Label>Email</Label>
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{profile.email}</span>
                    {profile.email_verified ? (
                      <Badge variant="default" className="ml-auto">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Verified
                      </Badge>
                    ) : (
                      <Badge variant="secondary" className="ml-auto">
                        <XCircle className="h-3 w-3 mr-1" />
                        Not Verified
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Member Since</Label>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">
                      {formatDate(profile.created_at)}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex gap-2 justify-end">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsEditing(false)}
                >
                  Cancel
                </Button>
                <Button type="submit">Save Changes</Button>
              </div>
            </form>
          ) : (
            <div className="space-y-6">
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-muted-foreground text-sm">
                      First Name
                    </Label>
                    <p className="font-medium">
                      {profile.firstname || "Not set"}
                    </p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground text-sm">
                      Last Name
                    </Label>
                    <p className="font-medium">
                      {profile.lastname || "Not set"}
                    </p>
                  </div>
                </div>

                <div>
                  <Label className="text-muted-foreground text-sm">
                    Username
                  </Label>
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <p className="font-medium">{profile.username}</p>
                  </div>
                </div>

                <Separator />

                <div>
                  <Label className="text-muted-foreground text-sm">Email</Label>
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <p className="font-medium">{profile.email}</p>
                    {profile.email_verified ? (
                      <Badge variant="default">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Verified
                      </Badge>
                    ) : (
                      <Badge variant="secondary">
                        <XCircle className="h-3 w-3 mr-1" />
                        Not Verified
                      </Badge>
                    )}
                  </div>
                </div>

                <div>
                  <Label className="text-muted-foreground text-sm">
                    Member Since
                  </Label>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <p className="font-medium">
                      {formatDate(profile.created_at)}
                    </p>
                  </div>
                </div>
              </div>

              <Separator />

              <div className="flex gap-2 justify-end">
                <Button variant="outline" onClick={() => navigate("/trips")}>
                  My Trips
                </Button>
                <Button onClick={() => setIsEditing(true)}>Edit Profile</Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
