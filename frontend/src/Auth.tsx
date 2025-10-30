import "./auth.css";
import { useState } from "react";
import { useNavigate } from "react-router";
import { serverBaseURL } from "./App";
import { storeTokens } from "./utils";

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
    <div>
      <form action={register}>
        <div>
          <label>Email</label>
        </div>
        <div>
          <input name="email" />
        </div>
        <div>
          <label>Choose a username</label>
        </div>
        <div>
          <input name="username" />
        </div>
        <div>
          <label>Password</label>
        </div>
        <div>
          <input type="password" name="password" />
        </div>
        <div>
          <label>Confirm password</label>
        </div>
        <div>
          <input type="password" name="c_password" />
        </div>
        <div>
          <button type="submit"> Sign Up</button>
        </div>
      </form>
    </div>
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
    <div>
      <form action={login}>
        <div>
          <label>Email</label>
        </div>
        <div>
          <input type="email" name="email" />
        </div>
        <div>
          <label>Password</label>
        </div>
        <div>
          <input type="password" name="password" />
        </div>
        <div>
          <button type="submit"> Log In</button>
        </div>
      </form>
    </div>
  );
}

export default function AuthCard() {
  const navigate = useNavigate();

  const [newUser, setUserStatus] = useState(false);
  const DisplayForm = newUser ? RegisterForm : LoginForm;
  return (
    <div className="auth-card">
      <button onClick={() => setUserStatus(!newUser)}>
        {newUser ? "Already have an account? Login" : "New user? Register"}
      </button>
      <DisplayForm
        onSuccess={() => {
          navigate("/dashboard");
        }}
      />
    </div>
  );
}
