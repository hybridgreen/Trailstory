import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { storeTokens, serverBaseURL, isAuthenticated } from "./utils";
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
  const [registering, setRegistering] = useState(false);
  const [match, setMatch] = useState(true);
  const [valid, setValid] = useState(true);

  function checkMatch(password: string, confirm: string) {
    if (password === confirm) {
      setMatch(true);
    } else {
      setMatch(false);
    }
  }

  function validatePassword(password: string) {
    const passwordRegex = /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$/;
    if (passwordRegex.test(password)) {
      setValid(true);
    } else {
      setValid(false);
    }
  }
  async function register(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    const email = formData.get("email") as string;
    const password = formData.get("password") as string;
    const username = formData.get("username") as string;

    if (!match) {
      toast.error("Passwords do not match");
      return;
    }

    const registrationData = new FormData();
    registrationData.append("email", email);
    registrationData.append("password", password);
    registrationData.append("username", username);

    try {
      setRegistering(true);
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
        toast.error(
          "Registration failed: " + (error.detail || "Unknown error")
        );
      }
    } catch (error) {
      console.error("Unknown error:", error);
    } finally {
      setRegistering(false);
    }
  }

  return (
    <Card className="flex flex-auto w-full max-w-md">
      <CardHeader>
        <CardTitle>Create an account</CardTitle>
        <CardDescription>Enter your details to sign up</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={register} className="space-y-4">
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
            <Input
              id="password"
              name="password"
              type="password"
              onChange={(e) => {
                const pwd = e.target.value;
                const confirm =
                  (document.getElementById("c_password") as HTMLInputElement)
                    ?.value || "";
                checkMatch(pwd, confirm);
                validatePassword(pwd);
              }}
              required
            />
          </div>
          {valid ? (
            <></>
          ) : (
            <Label>
              <p className="text-sm text-red-500">
                Min 8 characters with uppercase, lowercase, and number
              </p>
            </Label>
          )}
          <div className="space-y-2">
            <Label htmlFor="c_password">Confirm Password</Label>
            <Input
              id="c_password"
              name="c_password"
              type="password"
              onChange={(e) => {
                const confirm = e.target.value;
                const pwd =
                  (document.getElementById("password") as HTMLInputElement)
                    ?.value || "";
                checkMatch(pwd, confirm);
              }}
              required
            />
          </div>
          {match ? (
            <></>
          ) : (
            <Label>
              {" "}
              <p className="text-sm text-red-500">Passwords do not match</p>
            </Label>
          )}
          <Button type="submit" loading={registering} className="w-full">
            Sign Up
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

function LoginForm({ onSuccess }: { onSuccess: () => void }) {
  const [logingIn, setLogingIn] = useState(false);

  async function login(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const formData = new FormData(e.currentTarget);

    try {
      setLogingIn(true);

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
        toast.error("Login failed: " + (error.detail || "Unknown error"));
      }
    } catch (error) {
      console.error("Unknown error:", error);
    } finally {
      setLogingIn(false);
    }
  }

  return (
    <Card className="flex flex-auto w-full max-w-md">
      <CardHeader>
        <CardTitle>Welcome back</CardTitle>
        <CardDescription>Sign in to your account</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={login} className="space-y-4">
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
            <a href="/reset-password">Forgot your password?</a>
          </div>
          <Button type="submit" loading={logingIn} className="w-full">
            Log In
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

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

  useEffect(() => {
    if (isAuthenticated()) {
      navigate("/dashboard");
    }
  }, [navigate]);

  return (
    <div className="flex flex-col items-center gap-4 max-w-md mx-auto p-6">
      <Button onClick={() => setUserStatus(!newUser)}>
        {newUser ? "Already have an account? Login" : "New user? Register"}
      </Button>
      <DisplayForm
        onSuccess={() => {
          navigate("/dashboard");
        }}
      ></DisplayForm>
    </div>
  );
}

export function LoginRedirect() {
  const navigate = useNavigate();
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
