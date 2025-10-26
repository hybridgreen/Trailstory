//import { useState } from "react";
import Auth from "./Auth.tsx";

export default function App() {
  return (
    <div className="app-container">
      <NavBar />
      <div>
        <Auth />
      </div>
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
