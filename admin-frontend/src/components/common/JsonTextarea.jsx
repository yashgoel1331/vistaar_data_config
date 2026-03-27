import { useState } from 'react';

export default function JsonTextarea({
  label,
  onSubmit,
  loading,
  buttonLabel = 'Submit',
  placeholder = '{ "snapshot": { ... }, "note": "..." }',
  example,
}) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    try {
      const parsed = JSON.parse(text);
      onSubmit(parsed);
    } catch {
      alert('Invalid JSON. Please check syntax.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      {label && <label className="block text-sm font-medium text-gray-700">{label}</label>}
      {example && (
        <pre className="text-xs bg-gray-100 border border-gray-200 rounded p-3 whitespace-pre-wrap">
          {example}
        </pre>
      )}
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={6}
        placeholder={placeholder}
        className="w-full border border-gray-300 rounded px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-400"
      />
      <button
        type="submit"
        disabled={loading}
        className="px-4 py-2 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Sending...' : buttonLabel}
      </button>
    </form>
  );
}
