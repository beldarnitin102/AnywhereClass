
import type { Task } from "../types/task";

type TaskCardProps = {
  task: Task;
  onReview: (taskId: string, decision: "approve" | "reject") => void;
};

function TaskCard({ task, onReview }: TaskCardProps) {
  const readableStatus = task.status.replaceAll("_", " ");

  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold tracking-wide text-blue-700">
          {task.mode.toUpperCase()}
        </span>

        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
          {readableStatus}
        </span>
      </div>

      <h3 className="mt-4 text-lg font-semibold text-slate-900">
        {task.command}
      </h3>

      <p className="mt-2 text-sm text-slate-500">
        {new Date(task.created_at).toLocaleString()}
      </p>

      <div className="mt-5 rounded-xl bg-slate-50 p-4">
        <h4 className="font-semibold text-slate-800">Proposed workflow</h4>

        <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-slate-600">
          {task.plan.map((item, index) => (
            <li key={`${index}-${item}`}>{item}</li>
          ))}
        </ol>
      </div>

      {task.status === "awaiting_approval" && (
        <div className="mt-5 flex flex-wrap justify-end gap-3">
          <button
            type="button"
            onClick={() => onReview(task.id, "reject")}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            Reject
          </button>

          <button
            type="button"
            onClick={() => onReview(task.id, "approve")}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
          >
            Approve simulation
          </button>
        </div>
      )}
    </article>
  );
}

export default TaskCard;
