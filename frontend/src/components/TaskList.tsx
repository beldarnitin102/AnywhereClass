
import type { Task } from "../types/task";
import TaskCard from "./TaskCard";

type TaskListProps = {
  tasks: Task[];
  onReview: (taskId: string, decision: "approve" | "reject") => void;
};

function TaskList({ tasks, onReview }: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
        <h3 className="font-semibold text-slate-800">No tasks yet</h3>
        <p className="mt-2 text-sm text-slate-500">
          Enter an instruction above to prepare your first task.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onReview={onReview}
        />
      ))}
    </div>
  );
}

export default TaskList;
