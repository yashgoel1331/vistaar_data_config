export default function StatusAlert({ message, type = 'info', onClose }) {
  if (!message) return null;
  const colors = {
    success: 'bg-emerald-50 text-emerald-900 border-emerald-200',
    error: 'bg-red-50 text-red-900 border-red-200',
    info: 'bg-slate-50 text-slate-800 border-gray-200',
  };
  return (
    <div
      className={`flex items-start justify-between gap-3 rounded-lg border px-4 py-3 text-sm ${colors[type] || colors.info}`}
    >
      <span className="whitespace-pre-wrap break-words">{message}</span>
      {onClose && (
        <button
          type="button"
          onClick={onClose}
          className="shrink-0 font-semibold text-gray-500 hover:text-gray-800"
          aria-label="Dismiss"
        >
          ×
        </button>
      )}
    </div>
  );
}
