import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { serverBaseURL } from "../utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { toast } from "sonner";

function ResetPassword() {
  const [resetting, setResetting] = useState(false);

  async function reset(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    try {
      setResetting(true);

      const response = await fetch(`${serverBaseURL}/auth/password/reset/`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        toast.success(data["message"]);
      } else {
        const error = await response.json();
        console.error("Login failed:", error);
        toast.error("Login failed: " + error.detail);
      }
    } catch (error) {
      console.error("Unknown error:", error);
    } finally {
      setResetting(false);
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <Card className="w-full max-w-sm mx-auto ">
        <CardHeader>
          <CardTitle> Reset your password</CardTitle>
          <CardDescription>
            Enter your email below to reset your password
          </CardDescription>
          <CardContent>
            <form onSubmit={reset}>
              <div className="flex flex-col gap-6">
                <div className="grid gap-2 mt-4">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    name="email"
                    placeholder="me@example.com"
                    required
                  />
                </div>
              </div>
              <Button type="submit" loading={resetting} className="w-full mt-8">
                Reset Password
              </Button>
            </form>
          </CardContent>
        </CardHeader>
      </Card>
    </div>
  );
}

function NewPassword({ token }: { token: string }) {
  const navigate = useNavigate();
  const [sending, setSending] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    const password = formData.get("password") as string;
    const confirmPassword = formData.get("c_password") as string;

    if (password !== confirmPassword) {
      toast.error("Passwords do not match.");
      return;
    }

    const passwordData = new FormData();
    passwordData.append("password", password);

    try {
      setSending(true);

      const response = await fetch(
        `${serverBaseURL}/auth/password/confirm/?token=${token}`,
        {
          method: "POST",
          body: passwordData,
        }
      );

      if (response.ok) {
        navigate("/login");
      } else {
        const error = await response.json();
        toast.error(
          "Registration failed: " + (error.detail || "Unknown error")
        );
      }
    } catch (error) {
      console.error("Unknown error:", error);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <Card className="w-full max-w-md ">
        <CardHeader>
          <CardTitle>Choose a new password</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" name="password" type="password" required />
            </div>

            <div className="space-y-2">
              <Label htmlFor="c_password">Confirm Password</Label>
              <Input
                id="c_password"
                name="c_password"
                type="password"
                required
              />
            </div>

            <Button type="submit" loading={sending} className="w-full">
              Confirm
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

export default function ResetPasswordCard() {
  const [searchParams] = useSearchParams();
  const urlToken = searchParams.get("token");

  if (urlToken) {
    return <NewPassword token={urlToken} />;
  } else {
    return <ResetPassword />;
  }
}
