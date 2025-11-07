import Auth, { ResetPasswordCard } from "./Auth.tsx";
import Trips from "./Trips/TripsPage.tsx";
import DraftTrip from "./Trips/CreateTrip.tsx";
import EditTripPage from "./Trips/EditTrip.tsx";
import ProfilePage from "./Profile.tsx";
import ViewTripPage from "./Trips/ViewTripPage.tsx";

import { BrowserRouter, Routes, Route } from "react-router";
import { useNavigate } from "react-router";
import { removeTokens, isAuthenticated } from "./utils.tsx";

import { Button } from "@/components/ui/button";
import { toast, Toaster } from "sonner";
import { ThemeProvider } from "./components/theme-provider.tsx";
import { ModeToggle } from "./components/toggle-mode.tsx";

export default function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
      <Toaster position="top-center" />
      <BrowserRouter>
        <NavBar />
        <Routes>
          <Route path="/" element={<Auth />} />
          <Route path="/trips" element={<Trips />} />
          <Route path="/trips/new" element={<DraftTrip />} />
          <Route path="/trips/:id/edit" element={<EditTripPage />} />
          <Route path="/trips/:id" element={<ViewTripPage />} />
          <Route path="/profile/me" element={<ProfilePage />} />
          <Route path="/reset-password" element={<ResetPasswordCard />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

function NavBar() {
  const navigate = useNavigate();

  function loginButtonHandler() {
    if (isAuthenticated()) {
      removeTokens();
      localStorage.removeItem("user");
      navigate("/");
      toast.success("You have been logged out");
      return;
    } else {
      navigate("/");
    }
  }
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-logo">
          <a href="/" style={{ textDecoration: "none", color: "inherit" }}>
            Trailstory{" "}
          </a>
        </div>

        <div className="navbar-links">
          <a href="/trips">Dashboard</a>
          <a href="/trips">Trips</a>
          <a href="/profile/me">My Profile</a>
        </div>
        <div className="navbar-actions">
          {" "}
          <Button onClick={loginButtonHandler}>
            {" "}
            {isAuthenticated() ? "Logout" : "Login"}
          </Button>
          <ModeToggle />
        </div>
      </div>
    </nav>
  );
}
