import { useState } from 'react';

export default function AliasEnglishForm({ onPatch, onPut, onDelete, loading }) {
  const [canonical, setCanonical] = useState('');
  const [aliases, setAliases] = useState('');

  const entry = () => ({
    canonical: canonical.trim(),
    aliases: aliases.split(',').map((s) => s.trim()).filter(Boolean),
  });

  const handlePatch = (e) => {
    e.preventDefault();
    if (!canonical.trim() || !aliases.trim()) return;
    onPatch({ entry: entry() });
  };

  const handlePut = (e) => {
    e.preventDefault();
    if (!canonical.trim() || !aliases.trim()) return;
    onPut({ entry: entry() });
  };

  const handleDelete = (e) => {
    e.preventDefault();
    if (!canonical.trim()) return;
    onDelete({ entry: { key: canonical.trim() } });
  };

  return (
    <div className="space-y-3 border rounded p-4 bg-white">
      <h3 className="text-sm font-semibold text-gray-700">English alias actions</h3>
      <div>
        <label className="block text-xs text-gray-500 mb-1">canonical</label>
        <input value={canonical} onChange={(e) => setCanonical(e.target.value)}
          className="w-full border rounded px-3 py-2 text-sm" placeholder="e.g. udder" />
      </div>
      <div>
        <label className="block text-xs text-gray-500 mb-1">aliases (comma separated)</label>
        <input value={aliases} onChange={(e) => setAliases(e.target.value)}
          className="w-full border rounded px-3 py-2 text-sm" placeholder="alias1, alias2" />
      </div>
      <div className="flex gap-2 flex-wrap">
        <button type="button" onClick={handlePatch} disabled={loading || !canonical.trim()}
          className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50">
          {loading ? '...' : 'Append (PATCH)'}
        </button>
        <button type="button" onClick={handlePut} disabled={loading || !canonical.trim()}
          className="px-3 py-1.5 text-sm bg-amber-600 text-white rounded hover:bg-amber-700 disabled:opacity-50">
          {loading ? '...' : 'Replace (PUT)'}
        </button>
        <button type="button" onClick={handleDelete} disabled={loading || !canonical.trim()}
          className="px-3 py-1.5 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50">
          {loading ? '...' : 'Delete key'}
        </button>
      </div>
    </div>
  );
}
