//import { useState } from "react";
import Auth from "./Auth.tsx";
import Dashboard from "./Dashboard.tsx";
import { BrowserRouter, Routes, Route } from "react-router";

export default function App() {
  return (
    <div className="app-container">
      <BrowserRouter>
        <NavBar />
        <Routes>
          <Route path="/" element={<Auth />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

function NavBar() {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-logo">Trailstory</div>

        <div className="navbar-links">
          <a href="/dashboard">Dashboard</a>
          <a href="/trips">Trips</a>
          <a href="/profile">My Profile</a>
        </div>
      </div>
    </nav>
  );
}
