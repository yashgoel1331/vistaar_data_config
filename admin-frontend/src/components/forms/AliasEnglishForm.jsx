import { useState, useEffect } from 'react';

const fieldClass =
  'w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:border-brand-red focus:outline-none focus:ring-1 focus:ring-brand-red';

export default function AliasEnglishForm({ onPatch, onPut, loading }) {
  const [canonical, setCanonical] = useState('');
  const [aliases, setAliases] = useState('');

  const entry = () => ({
    canonical: canonical.trim(),
    aliases: aliases.split(',').map((s) => s.trim()).filter(Boolean),
  });

  return (
    <div className="flex h-full flex-col">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-gray-900">PATCH / PUT — Alias entry</h3>
        <p className="mt-1 text-sm text-gray-500">
          PATCH appends aliases; PUT replaces the full list for the canonical key.
        </p>
      </div>
      <div className="space-y-4">
        <div>
          <label className="mb-1.5 block text-xs font-medium text-gray-500">Canonical</label>
          <input
            type="text"
            value={canonical}
            onChange={(e) => setCanonical(e.target.value)}
            placeholder="e.g. udder"
            className={fieldClass}
          />
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-medium text-gray-500">Aliases</label>
          <input
            type="text"
            value={aliases}
            onChange={(e) => setAliases(e.target.value)}
            placeholder="Add alias (comma-separated)"
            className={fieldClass}
          />
        </div>
      </div>
      <div className="mt-6 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => {
            if (!canonical.trim() || !aliases.trim()) return;
            void Promise.resolve(onPatch({ entry: entry() }));
          }}
          disabled={loading || !canonical.trim() || !aliases.trim()}
          className="inline-flex rounded-lg bg-brand-red px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-brand-redhover disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? '…' : 'PATCH'}
        </button>
        <button
          type="button"
          onClick={() => {
            if (!canonical.trim() || !aliases.trim()) return;
            void Promise.resolve(onPut({ entry: entry() }));
          }}
          disabled={loading || !canonical.trim() || !aliases.trim()}
          className="inline-flex rounded-lg bg-brand-mustard px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-brand-mustardhover disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? '…' : 'PUT (replace)'}
        </button>
      </div>
    </div>
  );
}
