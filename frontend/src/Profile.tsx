import { useState, useEffect, useCallback } from "react";
import {
  isAuthenticated,
  isTokenExpiring,
  refreshTokens,
  serverBaseURL,
} from "./utils";
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
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

import { toast } from "sonner";
import { Spinner } from "./components/ui/spinner";
import { useNavigate } from "react-router";

interface UserProfile {
  id: string;
  email: string;
  username: string;
  firstname: string | null;
  lastname: string | null;
  email_verified: boolean;
  avatar_id: string | null;
  created_at: string;
}

function PasswordDialog() {
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    if (formData.get("new_password") !== formData.get("c_password")) {
      toast.error("Passwords do not match");
      return;
    }

    formData.delete("c_password");

    try {
      setSaving(true);

      const response = await fetch(`${serverBaseURL}/users/password/`, {
        method: "PUT",
        body: formData,
        headers: {
          authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (response.ok) {
        setOpen(false);
        toast.success("Password Changed");
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to change password");
      }
    } catch (error) {
      console.error("Unknown error:", error);
    } finally {
      setSaving(false);
    }
  }
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">Change password</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Change password</DialogTitle>
          <DialogDescription>
            Update your password here. Click save when you&apos;re done.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4">
            <div className="grid gap-3">
              <Label htmlFor="password-1">Current Password</Label>
              <Input
                id="password-1"
                name="old_password"
                placeholder="Enter password"
                type="password"
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="password-2">New Password</Label>
              <Input
                id="password-2"
                name="new_password"
                placeholder="Choose a new password"
                type="password"
              />
            </div>
            <div className="grid gap-3 mb-4">
              <Label htmlFor="password-3">Confirm Password</Label>
              <Input
                id="password-3"
                name="c_password"
                placeholder="Confirm new password"
                type="password"
              />
            </div>
          </div>

          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button type="submit" loading={saving}>
              Save changes
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function FileUploadDialog() {
  const [file, setFile] = useState<File | null>(null);
  const [open, setOpen] = useState(false);
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      console.log("Received file:", file);
      setFile(file);
    }
  };

  async function uploadAvatar() {
    if (!file) {
      toast.error("Please select a file");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${serverBaseURL}/users/avatar/`, {
        method: "POST",
        body: formData,
        headers: {
          authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (response.ok) {
        toast.success("Avatar updated");
        setOpen(false);
        window.location.reload();
      }
    } catch (error) {
      console.error("Unknown error:", error);
    }
  }
  return (
    <div>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button variant="outline">Edit avatar</Button>
        </DialogTrigger>
        <DialogDescription></DialogDescription>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Choose a new avatar</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <Input
              type="file"
              accept="image/*"
              name="avatar"
              onChange={handleFileChange}
            />
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline">Cancel</Button>
              </DialogClose>
              <Button onClick={uploadAvatar}>Upload</Button>
            </DialogFooter>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const navigate = useNavigate();

  const fetchProfile = useCallback(async () => {
    if (isTokenExpiring()) {
      await refreshTokens();
    }

    try {
      setLoading(true);
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
        toast.error("Failed to load profile");
      }
    } catch (error) {
      console.error("Error:", error);
      toast.error("Network error");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  async function handleSaveProfile(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (isTokenExpiring()) {
      await refreshTokens();
    }

    const formData = new FormData(event.currentTarget);

    try {
      setSaving(true);
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
        toast.success("Profile updated!");
      } else {
        const error = await response.json();
        console.error("Error:", error);
        toast.error("Failed to update profile");
      }
    } catch (error) {
      console.error("Error:", error);
      toast.error("Network error");
    } finally {
      setSaving(false);
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="flex flex-auto justify-center items-center">
        <Card>
          <CardContent>Please log in to see your profile</CardContent>
          <Button
            onClick={() => {
              navigate("/");
            }}
            className="m-auto w-fit"
          >
            {" "}
            Log In Now
          </Button>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex flex-auto justify-center items-center">
        <Spinner className="h-20 w-20" />
      </div>
    );
  }
  if (!profile) {
    return (
      <div className="flex flex-auto justify-center items-center">
        <Card>
          <CardContent>Profile not found</CardContent>
        </Card>
      </div>
    );
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
    <div className="max-w-2xl w-full mx-auto p-6">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <Avatar className="h-20 w-20">
              <AvatarImage
                src={profile.avatar_id || "https://github.com/shadcn.png"}
              />
              <AvatarFallback>
                {profile.firstname?.[0]}
                {profile.lastname?.[0]}
              </AvatarFallback>
            </Avatar>
            <FileUploadDialog />
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
                <Button loading={saving} type="submit">
                  Save Changes
                </Button>
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
                <PasswordDialog />
                <Button onClick={() => setIsEditing(true)}>Edit Profile</Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
