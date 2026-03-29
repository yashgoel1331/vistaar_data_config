const META_KEYS = new Set([
  'query',
  'match_type',
  'limit',
  'count',
  'returned',
  'error',
  '_http_status',
  'skipped',
  'ok',
  'message',
  'version',
  'versions',
  'new_count',
]);

function normalizePayload(data) {
  if (data == null) return { kind: 'empty' };

  if (Array.isArray(data)) {
    return data.length ? { kind: 'array', rows: data } : { kind: 'empty' };
  }

  if (typeof data === 'object') {
    if (data.error && !Array.isArray(data.data) && typeof data.data !== 'object') {
      return { kind: 'error', message: data.error };
    }

    if (Array.isArray(data.data)) {
      return data.data.length ? { kind: 'array', rows: data.data } : { kind: 'empty' };
    }

    if (data.data != null && typeof data.data === 'object' && !Array.isArray(data.data)) {
      return { kind: 'array', rows: [data.data] };
    }

    const entries = Object.entries(data).filter(([k]) => !META_KEYS.has(k));
    if (entries.length) {
      return { kind: 'kv', entries };
    }
  }

  return { kind: 'raw', value: data };
}

const EMPTY_MSG = 'Search for a term or view all entries to see results.';

export default function ResultsTable({ data, emptyMessage = EMPTY_MSG }) {
  const norm = normalizePayload(data);

  if (norm.kind === 'error') {
    return (
      <p className="py-12 text-center text-sm text-gray-500" role="status">
        {norm.message}
      </p>
    );
  }

  if (norm.kind === 'empty') {
    return <p className="py-12 text-center text-sm text-gray-400">{emptyMessage}</p>;
  }

  if (norm.kind === 'raw') {
    return (
      <pre className="max-h-96 overflow-auto rounded-lg bg-gray-50 p-4 text-xs text-gray-800">
        {JSON.stringify(norm.value, null, 2)}
      </pre>
    );
  }

  if (norm.kind === 'kv') {
    return (
      <div className="overflow-x-auto">
        <table className="w-full min-w-[320px] text-sm">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-600">
                Key
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-600">
                Value
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {norm.entries.map(([k, v]) => (
              <tr key={k} className="hover:bg-gray-50/80">
                <td className="px-4 py-3 font-mono text-sm text-brand-red">{k}</td>
                <td className="max-w-md truncate px-4 py-3 text-gray-800" title={formatCell(v)}>
                  {formatCell(v)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  const rows = norm.rows;
  const keys = [...new Set(rows.flatMap((row) => (row && typeof row === 'object' ? Object.keys(row) : [])))];

  if (!keys.length) {
    return <p className="py-12 text-center text-sm text-gray-400">{emptyMessage}</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[480px] text-sm">
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50">
            {keys.map((k) => (
              <th
                key={k}
                className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-600"
              >
                {humanizeKey(k)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {rows.map((row, i) => (
            <tr key={i} className="hover:bg-gray-50/80">
              {keys.map((k) => (
                <td key={k} className="max-w-xs px-4 py-3 align-top text-gray-800" title={formatCell(row?.[k])}>
                  {formatCell(row?.[k])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function humanizeKey(k) {
  return k.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatCell(val) {
  if (val === null || val === undefined) return '';
  if (typeof val === 'string') return val;
  return JSON.stringify(val);
}
