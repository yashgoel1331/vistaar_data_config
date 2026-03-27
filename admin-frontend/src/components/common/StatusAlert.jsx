export default function StatusAlert({ message, type = 'info', onClose }) {
  if (!message) return null;
  const colors = {
    success: 'bg-green-50 text-green-800 border-green-300',
    error:   'bg-red-50 text-red-800 border-red-300',
    info:    'bg-blue-50 text-blue-800 border-blue-300',
  };
  return (
    <div className={`border rounded px-4 py-3 mb-4 flex items-center justify-between text-sm ${colors[type] || colors.info}`}>
      <span className="whitespace-pre-wrap break-all">{message}</span>
      {onClose && (
        <button onClick={onClose} className="ml-4 font-bold opacity-60 hover:opacity-100">&times;</button>
      )}
    </div>
  );
}
