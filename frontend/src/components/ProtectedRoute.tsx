import { useEffect, useState, type ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { getCurrentUser, logoutUser } from "../services/api";

type ProtectedRouteProps = {
  children: ReactNode;
};

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const [checking, setChecking] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    let active = true;

    async function checkSession() {
      if (!sessionStorage.getItem("access_token")) {
        if (active) {
          setAuthenticated(false);
          setChecking(false);
        }
        return;
      }

      try {
        await getCurrentUser();

        if (active) {
          setAuthenticated(true);
        }
      } catch {
        logoutUser();

        if (active) {
          setAuthenticated(false);
        }
      } finally {
        if (active) {
          setChecking(false);
        }
      }
    }

    void checkSession();

    return () => {
      active = false;
    };
  }, []);

  if (checking) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-slate-600">Checking your session...</p>
      </main>
    );
  }

  if (!authenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

export default ProtectedRoute;
