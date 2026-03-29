import { useState, useEffect } from 'react';

const inputArea =
  'w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm font-mono text-gray-900 placeholder:text-gray-400 focus:border-brand-red focus:outline-none focus:ring-1 focus:ring-brand-red';

export default function JsonTextarea({
  title = 'POST — Add / Replace Config',
  subtitle = 'Use this to add new entries or replace entire config snapshot.',
  onSubmit,
  loading,
  buttonLabel = 'POST',
  placeholder = 'Paste full config JSON here...',
  example,
  resetVersion = 0,
}) {
  const [text, setText] = useState('');

  useEffect(() => {
    if (resetVersion === 0) return;
    setText('');
  }, [resetVersion]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    let parsed;
    try {
      parsed = JSON.parse(text);
    } catch {
      alert('Invalid JSON. Please check syntax.');
      return;
    }
    await Promise.resolve(onSubmit(parsed));
  };

  return (
    <form onSubmit={handleSubmit} className="flex h-full flex-col">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-gray-900">{title}</h3>
        {subtitle && <p className="mt-1 text-sm text-gray-500">{subtitle}</p>}
      </div>
      {example && (
        <div className="mb-4">
          <p className="mb-2 text-xs font-medium text-gray-500">Example format:</p>
          <pre className="max-h-48 overflow-auto rounded-lg border border-gray-100 bg-gray-50 p-3 text-xs text-gray-800 whitespace-pre-wrap">
            {example}
          </pre>
        </div>
      )}
      <label className="mb-2 text-sm font-medium text-gray-700">JSON Body</label>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={10}
        placeholder={placeholder}
        className={`${inputArea} min-h-[160px] flex-1`}
      />
      <button
        type="submit"
        disabled={loading}
        className="mt-4 inline-flex w-full justify-center rounded-lg bg-brand-red px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-brand-redhover disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
      >
        {loading ? 'Sending...' : buttonLabel}
      </button>
    </form>
  );
}
