import { useState, useMemo } from 'react';
import { IconTrash } from '../icons/Icons';

function normalizeRows(data) {
  if (data == null) return [];
  if (Array.isArray(data)) return data;
  if (Array.isArray(data.data)) return data.data;
  return [];
}

export default function GlossaryCards({ data, onEdit, onDelete, actionLoading }) {
  const [filter, setFilter] = useState('');
  const rows = useMemo(() => normalizeRows(data), [data]);

  const filtered = useMemo(() => {
    if (!filter.trim()) return rows;
    const q = filter.toLowerCase().trim();
    return rows.filter((r) => {
      const en = (r.en || '').toLowerCase();
      const gu = Array.isArray(r.gu) ? r.gu.join(' ').toLowerCase() : '';
      const tr = Array.isArray(r.transliteration) ? r.transliteration.join(' ').toLowerCase() : '';
      return en.includes(q) || gu.includes(q) || tr.includes(q);
    });
  }, [rows, filter]);

  if (!rows.length) {
    return (
      <p className="py-12 text-center text-sm text-gray-400">
        Search for a term or view all entries to see results.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filter bar */}
      <div className="relative">
        <svg
          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z" />
        </svg>
        <input
          type="text"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="Filter results..."
          className="w-full rounded-lg border border-gray-200 py-2 pl-9 pr-3 text-sm text-gray-700 placeholder-gray-400 transition focus:border-brand-red focus:outline-none focus:ring-1 focus:ring-brand-red"
        />
        {filter && (
          <button
            onClick={() => setFilter('')}
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-0.5 text-gray-400 hover:text-gray-600"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Count */}
      <p className="text-xs text-gray-500">
        Showing <span className="font-semibold text-gray-700">{filtered.length}</span>
        {filtered.length !== rows.length && <> of {rows.length}</>} entries
      </p>

      {/* Cards */}
      {filtered.length === 0 ? (
        <p className="py-8 text-center text-sm text-gray-400">No entries match your filter.</p>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((row, i) => (
            <GlossaryCard
              key={row.en || i}
              row={row}
              onEdit={onEdit}
              onDelete={onDelete}
              actionLoading={actionLoading}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function GlossaryCard({ row, onEdit, onDelete, actionLoading }) {
  const en = row.en || '—';
  const guList = Array.isArray(row.gu) ? row.gu : [];
  const trList = Array.isArray(row.transliteration) ? row.transliteration : [];

  return (
    <div className="group relative rounded-xl border border-gray-200 bg-white p-4 transition hover:border-brand-red/30 hover:shadow-md">
      {/* Action buttons */}
      <div className="absolute right-3 top-3 flex gap-1 opacity-0 transition group-hover:opacity-100">
        <button
          onClick={() => onEdit(row)}
          disabled={actionLoading}
          className="rounded-md p-1.5 text-gray-400 transition hover:bg-gray-100 hover:text-brand-red disabled:opacity-50"
          title="Edit"
        >
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125" />
          </svg>
        </button>
        <button
          onClick={() => onDelete(en)}
          disabled={actionLoading}
          className="rounded-md p-1.5 text-gray-400 transition hover:bg-red-50 hover:text-red-600 disabled:opacity-50"
          title="Delete"
        >
          <IconTrash className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* English term */}
      <h3 className="pr-16 text-base font-semibold text-gray-900">{en}</h3>

      {/* Gujarati */}
      {guList.length > 0 && (
        <div className="mt-2.5">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-gray-400">Gujarati</span>
          <div className="mt-1 flex flex-wrap gap-1.5">
            {guList.map((g, i) => (
              <span key={i} className="inline-block rounded-md bg-brand-redlight px-2 py-0.5 text-sm font-medium text-brand-red">
                {g}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Transliteration */}
      {trList.length > 0 && (
        <div className="mt-2.5">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-gray-400">Transliteration</span>
          <div className="mt-1 flex flex-wrap gap-1.5">
            {trList.map((t, i) => (
              <span key={i} className="inline-block rounded-md bg-amber-50 px-2 py-0.5 text-sm font-medium text-amber-700">
                {t}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
