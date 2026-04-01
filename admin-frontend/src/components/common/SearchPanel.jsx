import { useState, useEffect } from 'react';
import { IconSearch, IconList, IconX } from '../icons/Icons';

const inputClass =
  'w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:border-brand-red focus:outline-none focus:ring-1 focus:ring-brand-red';

export default function SearchPanel({
  onSearch,
  onViewAll,
  onClear,
  loading,
  defaultLimit = 10,
  searchPlaceholder = 'Search term...',
  resetVersion = 0,
  extraButtons = null,
}) {
  const [term, setTerm] = useState('');
  const [limit, setLimit] = useState(String(defaultLimit));

  useEffect(() => {
    if (resetVersion === 0) return;
    setTerm('');
    setLimit(String(defaultLimit));
  }, [resetVersion, defaultLimit]);

  const runSearch = () => onSearch(term.trim(), limit.trim() || undefined);

  return (
    <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div className="flex flex-1 flex-col gap-4 sm:flex-row sm:items-end">
        <div className="min-w-0 flex-1">
          <label className="mb-1.5 block text-xs font-medium text-gray-500">Search term</label>
          <input
            type="text"
            value={term}
            onChange={(e) => setTerm(e.target.value)}
            placeholder={searchPlaceholder}
            className={inputClass}
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), runSearch())}
          />
        </div>
        <div className="w-full sm:w-24">
          <label className="mb-1.5 block text-xs font-medium text-gray-500">Limit</label>
          <input
            type="text"
            inputMode="numeric"
            value={limit}
            onChange={(e) => setLimit(e.target.value)}
            className={inputClass}
          />
        </div>
      </div>
      <div className="flex flex-wrap items-center justify-end gap-2">
        <button
          type="button"
          onClick={runSearch}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg bg-brand-red px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-brand-redhover disabled:cursor-not-allowed disabled:opacity-50"
        >
          <IconSearch />
          {loading ? 'Searching...' : 'Search'}
        </button>
        <button
          type="button"
          onClick={() => onViewAll(limit.trim() || undefined)}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-800 shadow-sm transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <IconList />
          View All
        </button>
        <button
          type="button"
          onClick={() => {
            setTerm('');
            setLimit(String(defaultLimit));
            onClear();
          }}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg bg-brand-mustard px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-brand-mustardhover disabled:cursor-not-allowed disabled:opacity-50"
        >
          <IconX />
          Clear
        </button>
        {extraButtons}
      </div>
    </div>
  );
}
