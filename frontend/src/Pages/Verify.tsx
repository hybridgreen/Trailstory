import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { serverBaseURL, isAuthenticated } from "../utils";
import { toast } from "sonner";
import { Spinner } from "@/components/ui/spinner";
import { LoginRedirect } from "@/Pages/Auth";

function VerifyEmail({ token }: { token: string }) {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    async function verify() {
      setLoading(true);
      try {
        const response = await fetch(
          `${serverBaseURL}/auth/email/verify/confirm/?token=${token}`,
          { method: "POST" }
        );

        if (response.ok) {
          toast.success("Email verified");
          navigate("/");
        } else {
          const error = await response.json();
          toast.error(error.detail || "Verification failed");
          navigate("/profile/me");
        }
      } catch (error) {
        console.error("Unknown error:", error);
      } finally {
        setLoading(false);
      }
    }

    verify(); // Actually call it!
  }, [token, navigate]);

  if (!isAuthenticated()) {
    toast.error("Please login and try again");
    return <LoginRedirect />;
  }

  if (loading) {
    return (
      <div className="flex flex-auto justify-center items-center">
        <Spinner className="h-20 w-20" />
      </div>
    );
  }

  return <div></div>;
}

export function VerifyPage() {
  const [searchParams] = useSearchParams();
  const urlToken = searchParams.get("token");

  return <VerifyEmail token={urlToken || ""} />;
}
