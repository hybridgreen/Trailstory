import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { storeTokens, serverBaseURL } from "./utils";
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

export interface authResponse {
  access_token: string;
  refresh_token: string;
  user: userResponse;
  token_type: string;
  expires_in: number;
}

export interface userResponse {
  id: string;
  email: string;
  username: string;
  firstname: string | null;
  lastname: string | null;
  email_verified: boolean;
  created_at: number;
}

function setActiveUser(user_data: userResponse) {
  localStorage.setItem("user", JSON.stringify(user_data));
}

function RegisterForm({ onSuccess }: { onSuccess: () => void }) {
  async function register(formData: FormData) {
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;
    const username = formData.get("username") as string;
    const confirmPassword = formData.get("c_password") as string;

    if (password !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    const registrationData = new FormData();
    registrationData.append("email", email);
    registrationData.append("password", password);
    registrationData.append("username", username);

    try {
      const response = await fetch(`${serverBaseURL}/users/`, {
        method: "POST",
        body: registrationData,
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Registration successful:", data);
        storeTokens(data);
        setActiveUser(data.user);
        onSuccess();
      } else {
        const error = await response.json();
        console.error("Registration failed:", error);
        alert("Registration failed: " + (error.detail || "Unknown error"));
      }
    } catch (error) {
      console.error("Unknown error:", error);
    }
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Create an account</CardTitle>
        <CardDescription>Enter your details to sign up</CardDescription>
      </CardHeader>
      <CardContent>
        <form action={register} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="you@example.com"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="username">Username</Label>
            <Input
              id="username"
              name="username"
              placeholder="Choose a username"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input id="password" name="password" type="password" required />
          </div>

          <div className="space-y-2">
            <Label htmlFor="c_password">Confirm Password</Label>
            <Input id="c_password" name="c_password" type="password" required />
          </div>

          <Button type="submit" className="w-full">
            Sign Up
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

function LoginForm({ onSuccess }: { onSuccess: () => void }) {
  async function login(formData: FormData) {
    try {
      const response = await fetch(`${serverBaseURL}/auth/login/`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Login successful:", data);
        storeTokens(data);
        setActiveUser(data.user);
        onSuccess();
      } else {
        const error = await response.json();
        console.error("Login failed:", error);
        alert("Login failed: " + (error.detail || "Unknown error"));
      }
    } catch (error) {
      console.error("Unknown error:", error);
    }
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Welcome back</CardTitle>
        <CardDescription>Sign in to your account</CardDescription>
      </CardHeader>
      <CardContent>
        <form action={login} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="you@example.com"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input id="password" name="password" type="password" required />
          </div>
          <div className="ml-auto inline-block text-sm underline-offset-4 hover:underline">
            <a href="/reset-password"> Forgot your password?</a>
          </div>
          <Button type="submit" className="w-full">
            Log In
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

function ResetPassword() {
  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    await resetPasswordAction(formData);
  }

  async function resetPasswordAction(formData: FormData) {
    try {
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
        alert("Login failed: " + error.detail);
      }
    } catch (error) {
      console.error("Unknown error:", error);
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
            <form onSubmit={handleSubmit}>
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
              <Button type="submit" className="w-full mt-8">
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

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    await sendPassword(formData);
  }
  async function sendPassword(formData: FormData) {
    const password = formData.get("password") as string;
    const confirmPassword = formData.get("c_password") as string;

    if (password !== confirmPassword) {
      toast.error("Passwords do not match.");
      return;
    }

    const passwordData = new FormData();
    passwordData.append("password", password);

    try {
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
        alert("Registration failed: " + (error.detail || "Unknown error"));
      }
    } catch (error) {
      console.error("Unknown error:", error);
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

            <Button type="submit" className="w-full">
              Confirm
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

export function ResetPasswordCard() {
  const [searchParams] = useSearchParams();
  const urlToken = searchParams.get("token");

  if (urlToken) {
    return <NewPassword token={urlToken} />;
  } else {
    return <ResetPassword />;
  }
}

export default function AuthCard() {
  const navigate = useNavigate();

  const [newUser, setUserStatus] = useState(false);
  const DisplayForm = newUser ? RegisterForm : LoginForm;
  return (
    <div className="auth-card flex flex-col items-center gap-4 max-w-md mx-auto p-6">
      <Button onClick={() => setUserStatus(!newUser)}>
        {newUser ? "Already have an account? Login" : "New user? Register"}
      </Button>
      <DisplayForm
        onSuccess={() => {
          navigate("/dashboard");
        }}
      />
    </div>
  );
}
