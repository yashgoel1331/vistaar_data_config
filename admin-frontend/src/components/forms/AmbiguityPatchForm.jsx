import { useState } from 'react';

export default function AmbiguityPatchForm({ onSubmit, loading }) {
  const [guTerms, setGuTerms] = useState('');
  const [type, setType] = useState('ask');
  const [rule, setRule] = useState('');
  const [context, setContext] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const terms = guTerms.split(',').map((s) => s.trim()).filter(Boolean);
    if (!terms.length || !rule.trim()) return;
    const entry = { gu_terms: terms, type, rule: rule.trim() };
    if (context.trim()) entry.context = context.trim();
    onSubmit({ entry });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3 border rounded p-4 bg-white">
      <h3 className="text-sm font-semibold text-gray-700">Add ambiguous_terms entry (PATCH)</h3>
      <div>
        <label className="block text-xs text-gray-500 mb-1">gu_terms (comma separated)</label>
        <input value={guTerms} onChange={(e) => setGuTerms(e.target.value)}
          className="w-full border rounded px-3 py-2 text-sm" placeholder="term1, term2" />
      </div>
      <div className="flex gap-3">
        <div className="flex-1">
          <label className="block text-xs text-gray-500 mb-1">type</label>
          <select value={type} onChange={(e) => setType(e.target.value)}
            className="w-full border rounded px-3 py-2 text-sm">
            <option value="ask">ask</option>
            <option value="hardcode">hardcode</option>
          </select>
        </div>
        <div className="flex-1">
          <label className="block text-xs text-gray-500 mb-1">rule</label>
          <input value={rule} onChange={(e) => setRule(e.target.value)}
            className="w-full border rounded px-3 py-2 text-sm" placeholder="Describe rule..." />
        </div>
      </div>
      <div>
        <label className="block text-xs text-gray-500 mb-1">context (optional)</label>
        <input value={context} onChange={(e) => setContext(e.target.value)}
          className="w-full border rounded px-3 py-2 text-sm" />
      </div>
      <button type="submit" disabled={loading}
        className="px-4 py-2 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50">
        {loading ? 'Adding...' : 'Add entry (PATCH)'}
      </button>
    </form>
  );
}
