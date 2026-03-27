export default function ResultsTable({ data }) {
  if (!data || (Array.isArray(data) && data.length === 0)) {
    return <p className="text-sm text-gray-400 italic">No results.</p>;
  }

  if (Array.isArray(data)) {
    const keys = [...new Set(data.flatMap((row) => Object.keys(row)))];
    return (
      <div className="overflow-x-auto border rounded max-h-96 overflow-y-auto">
        <table className="w-full text-sm text-left">
          <thead className="bg-gray-100 sticky top-0">
            <tr>
              {keys.map((k) => (
                <th key={k} className="px-3 py-2 font-medium text-gray-600 border-b">{k}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i} className="border-b hover:bg-gray-50">
                {keys.map((k) => (
                  <td key={k} className="px-3 py-2 align-top max-w-xs truncate" title={formatCell(row[k])}>
                    {formatCell(row[k])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (typeof data === 'object') {
    const entries = Object.entries(data);
    return (
      <div className="overflow-x-auto border rounded max-h-96 overflow-y-auto">
        <table className="w-full text-sm text-left">
          <thead className="bg-gray-100 sticky top-0">
            <tr>
              <th className="px-3 py-2 font-medium text-gray-600 border-b">Key</th>
              <th className="px-3 py-2 font-medium text-gray-600 border-b">Value</th>
            </tr>
          </thead>
          <tbody>
            {entries.map(([k, v]) => (
              <tr key={k} className="border-b hover:bg-gray-50">
                <td className="px-3 py-2 font-mono text-indigo-700">{k}</td>
                <td className="px-3 py-2 max-w-md truncate" title={formatCell(v)}>{formatCell(v)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return <pre className="text-xs bg-gray-100 p-3 rounded overflow-auto max-h-64">{JSON.stringify(data, null, 2)}</pre>;
}

function formatCell(val) {
  if (val === null || val === undefined) return '';
  if (typeof val === 'string') return val;
  return JSON.stringify(val);
}
