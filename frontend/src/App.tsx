import Auth from "./Auth.tsx";
import Trips from "./Trips/TripsPage.tsx";
import DraftTrip from "./Trips/CreateTrip.tsx";
import EditTripPage from "./Trips/EditTrip.tsx";
import ProfilePage from "./Profile.tsx";
import ViewTripPage from "./Trips/ViewTripPage.tsx";

import { BrowserRouter, Routes, Route } from "react-router";
import { useNavigate } from "react-router";
import { removeTokens, isAuthenticated } from "./utils.tsx";

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
          <Route path="/trips/:id" element={<ViewTripPage />} />
          <Route path="/profile/me" element={<ProfilePage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

function NavBar() {
  const navigate = useNavigate();

  function loginButtonHandler() {
    if (isAuthenticated()) {
      removeTokens();
      localStorage.removeItem("user");
      alert("You have been logged out");
      navigate("/");
      return;
    } else {
      navigate("/");
    }
  }
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-logo">
          <a href="/">Trailstory </a>
        </div>

        <div className="navbar-links">
          <a href="/trips">Trips</a>
          <a href="/profile/me">My Profile</a>
          <button onClick={loginButtonHandler}>
            {" "}
            {isAuthenticated() ? "Logout" : "Login"}
          </button>
        </div>
      </div>
    </nav>
  );
}
