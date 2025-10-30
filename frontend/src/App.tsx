//import { useState } from "react";
import Auth from "./Auth.tsx";

import Trips from "./TripsPage.tsx";
import DraftTrip from "./CreateTrip.tsx";
import EditTripPage from "./EditTrip.tsx";
import { BrowserRouter, Routes, Route } from "react-router";
import { useNavigate } from "react-router";
import { removeTokens } from "./utils.tsx";

export const serverBaseURL = "http://127.0.0.1:8000";
export const clientBaseURL = "http://localhost:5173";

export default function App() {
  return (
    <div className="app-container">
      <BrowserRouter>
        <NavBar />
        <Routes>
          <Route path="/" element={<Auth />} />
          <Route path="/trips" element={<Trips />} />
          <Route path="/trips/new" element={<DraftTrip />} />
          <Route path="/trips/:id/edit" element={<EditTripPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

function NavBar() {
  const navigate = useNavigate();

  function logoutHandler() {
    removeTokens();
    localStorage.removeItem("user");
    alert("You have been logged out");
    navigate("/");
  }
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-logo">
          <a href="/">Trailstory </a>
        </div>

        <div className="navbar-links">
          <a href="/dashboard">Dashboard</a>
          <a href="/trips">Trips</a>
          <a href="/profile">My Profile</a>
          <button onClick={logoutHandler}> Logout</button>
        </div>
      </div>
    </nav>
  );
}
