import { useState, useEffect } from 'react';

const fieldClass =
  'w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:border-brand-red focus:outline-none focus:ring-1 focus:ring-brand-red';

export default function AmbiguityPatchForm({ onSubmit, loading, resetVersion = 0 }) {
  const [guTerms, setGuTerms] = useState('');
  const [type, setType] = useState('ask');
  const [rule, setRule] = useState('');
  const [context, setContext] = useState('');

  useEffect(() => {
    if (resetVersion === 0) return;
    setGuTerms('');
    setType('ask');
    setRule('');
    setContext('');
  }, [resetVersion]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const terms = guTerms.split(',').map((s) => s.trim()).filter(Boolean);
    if (!terms.length || !rule.trim()) return;
    const entry = { gu_terms: terms, type, rule: rule.trim() };
    if (context.trim()) entry.context = context.trim();
    await Promise.resolve(onSubmit({ entry }));
  };

  return (
    <form onSubmit={handleSubmit} className="flex h-full flex-col">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-gray-900">PATCH — Add rule</h3>
        <p className="mt-1 text-sm text-gray-500">Appends one validated entry to ambiguous_terms.</p>
      </div>
      <div className="space-y-4">
        <div>
          <label className="mb-1.5 block text-xs font-medium text-gray-500">Gujarati terms (comma separated)</label>
          <input
            type="text"
            value={guTerms}
            onChange={(e) => setGuTerms(e.target.value)}
            placeholder="term1, term2"
            className={fieldClass}
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-gray-500">Type</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className={fieldClass}
            >
              <option value="ask">ask</option>
              <option value="hardcode">hardcode</option>
            </select>
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-gray-500">Rule</label>
            <input
              type="text"
              value={rule}
              onChange={(e) => setRule(e.target.value)}
              placeholder="Describe rule..."
              className={fieldClass}
            />
          </div>
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-medium text-gray-500">Context (optional)</label>
          <input type="text" value={context} onChange={(e) => setContext(e.target.value)} className={fieldClass} />
        </div>
      </div>
      <button
        type="submit"
        disabled={loading}
        className="mt-6 inline-flex w-full justify-center rounded-lg bg-brand-red px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-brand-redhover disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
      >
        {loading ? 'Adding...' : 'PATCH'}
      </button>
    </form>
  );
}
