import type { authResponse, userResponse } from "./Auth";

export const serverBaseURL = import.meta.env.VITE_SERVER_URL;
export const clientBaseURL = import.meta.env.VITE_CLIENT_URL;

export function isTokenExpiring() {
  const expiry = localStorage.getItem("token_expiry");
  if (!expiry) return true;

  const expiryTime = parseInt(expiry);
  const now = Date.now();
  const fiveMinutes = 5 * 60 * 1000;

  return expiryTime - now < fiveMinutes;
}

export function removeTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export async function refreshTokens() {
  const response = await fetch(serverBaseURL + "/auth/refresh", {
    method: "GET",
    headers: {
      authorization: `Bearer ${localStorage.getItem("refresh_token")}`,
    },
  });

  if (response.ok) {
    const data = await response.json();
    storeTokens(data);
  } else {
    const error = await response.json();
    console.error("Token refresh failed:", error);
  }
}

export const isAuthenticated = () => {
  return localStorage.getItem("access_token") !== null;
};

export function getActiveUser() {
  return JSON.parse(localStorage.getItem("user") as string) as userResponse;
}

export async function fetchUser(userID: string): Promise<userResponse | null> {
  try {
    const response = await fetch(`${serverBaseURL}/users/${userID}`, {
      method: "GET",
    });
    if (response.ok) {
      const user = await response.json();
      console.log("Fetched user", user);
      return user;
    } else {
      const error = await response.json();
      console.error("Error:", error);
      return null;
    }
  } catch (error) {
    console.error("Unknown error:", error);
    return null;
  }
}

export function storeTokens(data: authResponse) {
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("refresh_token", data.refresh_token);

  const expiryTime = Date.now() + data.expires_in * 1000;
  localStorage.setItem("token_expiry", expiryTime.toString());
}
