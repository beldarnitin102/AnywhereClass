
import { useCallback, useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

type Task = {
  id: string;
  command: string;
  status: string;
  created_at: string;
  plan: string[];
  mode: string;
};

function readableStatus(status: string) {
  return status.replaceAll("_", " ");
}

function App() {
  const [command, setCommand] = useState("");
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const loadTasks = useCallback(async () => {
    try {
      const response = await fetch(`${API}/api/v1/tasks`);
      if (!response.ok) throw new Error("Could not load tasks.");
      setTasks(await response.json());
    } catch {
      setError("Cannot connect to the backend. Is FastAPI running?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadTasks();
  }, [loadTasks]);

  async function createTask(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (command.trim().length < 5) return;

    setSubmitting(true);
    setError("");

    try {
      const response = await fetch(`${API}/api/v1/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: command.trim() }),
      });

      if (!response.ok) {
        throw new Error("Could not create the task.");
      }

      const task: Task = await response.json();
      setTasks((previous) => [task, ...previous]);
      setCommand("");
    } catch {
      setError("Task creation failed. Check that the backend is running.");
    } finally {
      setSubmitting(false);
    }
  }

  async function reviewTask(
    taskId: string,
    decision: "approve" | "reject",
  ) {
    setError("");

    try {
      const response = await fetch(
        `${API}/api/v1/tasks/${taskId}/decision`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ decision }),
        },
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail ?? "Could not review task.");
      }

      setTasks((previous) =>
        previous.map((task) => task.id === taskId ? result : task),
      );
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Something went wrong.",
      );
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-icon">A</span>
          <span>ActionPilot <small>AI WORKSPACE</small></span>
        </a>
        <span className="environment">
          <span className="status-dot" /> Local development
        </span>
      </header>

      <section className="hero">
        <p className="eyebrow">YOUR AI ACTION WORKSPACE</p>
        <h1>What would you like<br />to get done?</h1>
        <p className="hero-copy">
          Describe a task in plain language. Review the plan before
          approving any action.
        </p>

        <form className="command-form" onSubmit={createTask}>
          <label htmlFor="command">Your instruction</label>
          <textarea
            id="command"
            value={command}
            onChange={(event) => setCommand(event.target.value)}
            placeholder="For example: Prepare a 10-question Data Structures quiz..."
            maxLength={2000}
            rows={4}
          />
          <div className="form-footer">
            <span>{command.length}/2000 characters</span>
            <button
              type="submit"
              disabled={submitting || command.trim().length < 5}
            >
              {submitting ? "Preparing..." : "Prepare task →"}
            </button>
          </div>
        </form>

        <div className="safety-note">
          <span>✓</span>
          Nothing is published or executed in this simulation.
        </div>
      </section>

      {error && <div className="error-banner" role="alert">{error}</div>}

      <section className="tasks-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">WORKFLOW</p>
            <h2>Recent tasks</h2>
          </div>
          <span className="task-count">{tasks.length} tasks</span>
        </div>

        {loading ? (
          <p className="empty-state">Loading tasks...</p>
        ) : tasks.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">↗</span>
            <h3>Your workspace is ready</h3>
            <p>Enter your first instruction above to create a task.</p>
          </div>
        ) : (
          <div className="task-list">
            {tasks.map((task) => (
              <article className="task-card" key={task.id}>
                <div className="task-card-header">
                  <span className="task-mode">SIMULATION</span>
                  <span className={`status status-${task.status}`}>
                    {readableStatus(task.status)}
                  </span>
                </div>

                <h3>{task.command}</h3>
                <p className="task-date">
                  {new Date(task.created_at).toLocaleString()}
                </p>

                <div className="plan">
                  <h4>Proposed workflow</h4>
                  <ol>
                    {task.plan.map((item) => <li key={item}>{item}</li>)}
                  </ol>
                </div>

                {task.status === "awaiting_approval" && (
                  <div className="task-actions">
                    <button
                      className="button-secondary"
                      onClick={() => void reviewTask(task.id, "reject")}
                    >
                      Reject
                    </button>
                    <button
                      onClick={() => void reviewTask(task.id, "approve")}
                    >
                      Approve simulation
                    </button>
                  </div>
                )}
              </article>
            ))}
          </div>
        )}
      </section>

      <footer>
        ActionPilot · Development prototype · Moodle not connected
      </footer>
    </main>
  );
}

export default App;
