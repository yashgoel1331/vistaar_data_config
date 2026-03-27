import { useState } from 'react';

export default function KeyValuePatchForm({ onPatch, onDelete, loading, title = 'Edit key' }) {
  const [key, setKey] = useState('');
  const [value, setValue] = useState('');

  const handlePatch = (e) => {
    e.preventDefault();
    if (!key.trim()) return;
    let parsed = value;
    try { parsed = JSON.parse(value); } catch { /* keep as string */ }
    onPatch({ entry: { key: key.trim(), value: parsed } });
  };

  const handleDelete = (e) => {
    e.preventDefault();
    if (!key.trim()) return;
    onDelete({ entry: { key: key.trim() } });
  };

  return (
    <form className="space-y-3 border rounded p-4 bg-white">
      <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
      <div>
        <label className="block text-xs text-gray-500 mb-1">Key</label>
        <input value={key} onChange={(e) => setKey(e.target.value)}
          className="w-full border rounded px-3 py-2 text-sm" placeholder="e.g. milk" />
      </div>
      <div>
        <label className="block text-xs text-gray-500 mb-1">Value (string or JSON)</label>
        <textarea value={value} onChange={(e) => setValue(e.target.value)} rows={3}
          className="w-full border rounded px-3 py-2 text-sm font-mono" placeholder='e.g. "replacement" or {"gu":["દૂધ"]}' />
      </div>
      <div className="flex gap-2">
        <button type="button" onClick={handlePatch} disabled={loading || !key.trim()}
          className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50">
          {loading ? 'Saving...' : 'Edit (PATCH)'}
        </button>
        <button type="button" onClick={handleDelete} disabled={loading || !key.trim()}
          className="px-3 py-1.5 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50">
          {loading ? 'Deleting...' : 'Delete'}
        </button>
      </div>
    </form>
  );
}
