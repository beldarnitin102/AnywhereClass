
import type { FormEvent } from "react";

type CommandFormProps = {
  command: string;
  submitting: boolean;
  onCommandChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

function CommandForm({
  command,
  submitting,
  onCommandChange,
  onSubmit,
}: CommandFormProps) {
  return (
    <form
      onSubmit={onSubmit}
      className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
    >
      <label
        htmlFor="command"
        className="mb-2 block text-sm font-semibold text-slate-800"
      >
        Your instruction
      </label>

      <textarea
        id="command"
        value={command}
        onChange={(event) => onCommandChange(event.target.value)}
        placeholder="For example: Prepare a 10-question Data Structures quiz..."
        maxLength={2000}
        rows={4}
        className="w-full resize-y rounded-xl border border-slate-300 p-3 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
      />

      <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
        <span className="text-xs text-slate-500">
          {command.length}/2000 characters
        </span>

        <button
          type="submit"
          disabled={submitting || command.trim().length < 5}
          className="rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {submitting ? "Preparing..." : "Prepare task →"}
        </button>
      </div>
    </form>
  );
}

export default CommandForm;
