import { apiRequest } from "../services/api";
import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";
import "../App.css";

import CommandForm from "../components/CommandForm";
import TaskList from "../components/TaskList";
import type { Task } from "../types/task";


function DashboardPage() {
  const [command, setCommand] = useState("");
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const loadTasks = useCallback(async () => {
  try {
    const data = await apiRequest<Task[]>("/api/v1/tasks");
    setTasks(data);
    setError("");
  } catch {
    setError("Cannot load tasks. Check the backend connection.");
  } finally {
    setLoading(false);
  }
}, []);

  useEffect(() => {
    void loadTasks();
  }, [loadTasks]);

  async function createTask(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();

  if (command.trim().length < 5) return;

  setSubmitting(true);
  setError("");

  try {
    const task = await apiRequest<Task>("/api/v1/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command: command.trim() }),
    });

    setTasks((previous) => [task, ...previous]);
    setCommand("");
  } catch (error) {
    setError(
      error instanceof Error ? error.message : "Task creation failed.",
    );
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
    const updatedTask = await apiRequest<Task>(
      `/api/v1/tasks/${taskId}/decision`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision }),
      },
    );

    setTasks((previous) =>
      previous.map((task) =>
        task.id === taskId ? updatedTask : task,
      ),
    );
  } catch (error) {
    setError(
      error instanceof Error ? error.message : "Something went wrong.",
    );
  }
}

  return (
    <>
      <section className="hero">
        <p className="eyebrow">YOUR AI ACTION WORKSPACE</p>

        <h1>
          What would you like
          <br />
          to get done?
        </h1>

        <p className="hero-copy">
          Describe a task in plain language. Review the plan before approving
          any action.
        </p>

        <CommandForm
          command={command}
          submitting={submitting}
          onCommandChange={setCommand}
          onSubmit={createTask}
        />

        <div className="safety-note">
          <span>✓</span>
          Nothing is published or executed in this simulation.
        </div>
      </section>

      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}

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
          <TaskList tasks={tasks} onReview={reviewTask} />
        )}
      </section>

      <footer>
        ActionPilot · Development prototype · Moodle not connected
      </footer>
    </>
  );
}

export default DashboardPage;
