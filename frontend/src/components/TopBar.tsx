
import { useNavigate } from "react-router-dom";
import { logoutUser } from "../services/api";

function TopBar() {
  const navigate = useNavigate();

  function handleLogout() {
    logoutUser();
    navigate("/login", { replace: true });
  }

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            ActionPilot
          </h1>
          <p className="text-xs text-slate-500">
            AI-powered task workspace
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="hidden rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700 sm:inline-flex">
            SIMULATION MODE
          </span>

          <button
            type="button"
            onClick={handleLogout}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
          >
            Log out
          </button>
        </div>
      </div>
    </header>
  );
}

export default TopBar;
