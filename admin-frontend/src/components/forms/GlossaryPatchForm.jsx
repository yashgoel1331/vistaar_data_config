import { useState, useEffect } from 'react';

const fieldClass =
  'w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:border-brand-red focus:outline-none focus:ring-1 focus:ring-brand-red';

export default function GlossaryPatchForm({ onPatch, loading, resetVersion = 0 }) {
  const [en, setEn] = useState('');
  const [guList, setGuList] = useState(['']);
  const [trList, setTrList] = useState(['']);

  useEffect(() => {
    if (resetVersion === 0) return;
    setEn('');
    setGuList(['']);
    setTrList(['']);
  }, [resetVersion]);

  const addGu = () => setGuList((s) => [...s, '']);
  const addTr = () => setTrList((s) => [...s, '']);

  const setGu = (i, v) => setGuList((s) => s.map((x, j) => (j === i ? v : x)));
  const setTr = (i, v) => setTrList((s) => s.map((x, j) => (j === i ? v : x)));

  const submit = async (e) => {
    e.preventDefault();
    if (!en.trim()) return;
    const gu = guList.map((s) => s.trim()).filter(Boolean);
    const transliteration = trList.map((s) => s.trim()).filter(Boolean);
    const value = {};
    if (gu.length) value.gu = gu;
    if (transliteration.length) value.transliteration = transliteration;
    await Promise.resolve(onPatch({ entry: { key: en.trim(), value } }));
  };

  return (
    <form onSubmit={submit} className="flex h-full flex-col">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-gray-900">PATCH — Update Existing Entry</h3>
        <p className="mt-1 text-sm text-gray-500">Use POST to add new entries. PATCH updates existing ones.</p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="mb-1.5 block text-xs font-medium text-gray-500">English Term</label>
          <input
            type="text"
            value={en}
            onChange={(e) => setEn(e.target.value)}
            placeholder="e.g. milk"
            className={fieldClass}
          />
        </div>

        <div>
          <label className="mb-1.5 block text-xs font-medium text-gray-500">Gujarati Terms</label>
          {guList.map((v, i) => (
            <div key={`gu-${i}`} className="mb-2 flex gap-2">
              <input
                type="text"
                value={v}
                onChange={(e) => setGu(i, e.target.value)}
                placeholder="Add Gujarati term"
                className={fieldClass}
              />
              {i === guList.length - 1 && (
                <button
                  type="button"
                  onClick={addGu}
                  className="shrink-0 rounded-lg border border-gray-300 px-3 text-lg font-medium text-gray-600 hover:bg-gray-50"
                  aria-label="Add Gujarati term"
                >
                  +
                </button>
              )}
            </div>
          ))}
        </div>

        <div>
          <label className="mb-1.5 block text-xs font-medium text-gray-500">Transliteration</label>
          {trList.map((v, i) => (
            <div key={`tr-${i}`} className="mb-2 flex gap-2">
              <input
                type="text"
                value={v}
                onChange={(e) => setTr(i, e.target.value)}
                placeholder="Add transliteration"
                className={fieldClass}
              />
              {i === trList.length - 1 && (
                <button
                  type="button"
                  onClick={addTr}
                  className="shrink-0 rounded-lg border border-gray-300 px-3 text-lg font-medium text-gray-600 hover:bg-gray-50"
                  aria-label="Add transliteration"
                >
                  +
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !en.trim()}
        className="mt-6 inline-flex w-full justify-center rounded-lg bg-brand-red px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-brand-redhover disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
      >
        {loading ? 'Saving...' : 'PATCH'}
      </button>
    </form>
  );
}
