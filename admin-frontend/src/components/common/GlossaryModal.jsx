import { useState, useEffect } from 'react';

const fieldClass =
  'w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:border-brand-red focus:outline-none focus:ring-1 focus:ring-brand-red';

export default function GlossaryModal({ open, onClose, onSubmit, loading, initial }) {
  const isEdit = !!initial;
  const [en, setEn] = useState('');
  const [guList, setGuList] = useState(['']);
  const [trList, setTrList] = useState(['']);

  useEffect(() => {
    if (open && initial) {
      setEn(initial.en || '');
      const gu = Array.isArray(initial.gu) ? initial.gu : [];
      const tr = Array.isArray(initial.transliteration) ? initial.transliteration : [];
      setGuList(gu.length ? [...gu] : ['']);
      setTrList(tr.length ? [...tr] : ['']);
    } else if (open) {
      setEn('');
      setGuList(['']);
      setTrList(['']);
    }
  }, [open, initial]);

  if (!open) return null;

  const setGu = (i, v) => setGuList((s) => s.map((x, j) => (j === i ? v : x)));
  const setTr = (i, v) => setTrList((s) => s.map((x, j) => (j === i ? v : x)));
  const removeGu = (i) => setGuList((s) => s.length > 1 ? s.filter((_, j) => j !== i) : s);
  const removeTr = (i) => setTrList((s) => s.length > 1 ? s.filter((_, j) => j !== i) : s);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!en.trim()) return;
    const gu = guList.map((s) => s.trim()).filter(Boolean);
    const transliteration = trList.map((s) => s.trim()).filter(Boolean);
    const value = {};
    if (gu.length) value.gu = gu;
    if (transliteration.length) value.transliteration = transliteration;

    if (isEdit) {
      await onSubmit({ entry: { key: en.trim(), value } });
    } else {
      const snapshot = {};
      snapshot[en.trim()] = value;
      await onSubmit({ snapshot });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="relative mx-4 w-full max-w-lg rounded-2xl border border-gray-200 bg-white p-6 shadow-xl">
        {/* Header */}
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">
            {isEdit ? 'Edit Entry' : 'Add New Entry'}
          </h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-gray-400 transition hover:bg-gray-100 hover:text-gray-600"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* English */}
          <div>
            <label className="mb-1.5 block text-xs font-medium text-gray-500">English Term</label>
            <input
              type="text"
              value={en}
              onChange={(e) => setEn(e.target.value)}
              placeholder="e.g. milk"
              className={fieldClass}
              readOnly={isEdit}
              autoFocus={!isEdit}
            />
            {isEdit && (
              <p className="mt-1 text-xs text-gray-400">Term cannot be changed. Delete and re-add to rename.</p>
            )}
          </div>

          {/* Gujarati */}
          <div>
            <label className="mb-1.5 block text-xs font-medium text-gray-500">Gujarati Terms</label>
            <div className="space-y-2">
              {guList.map((v, i) => (
                <div key={`gu-${i}`} className="flex gap-2">
                  <input
                    type="text"
                    value={v}
                    onChange={(e) => setGu(i, e.target.value)}
                    placeholder="Gujarati term"
                    className={fieldClass}
                  />
                  {guList.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeGu(i)}
                      className="shrink-0 rounded-lg px-2 text-gray-400 transition hover:bg-red-50 hover:text-red-500"
                    >
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 12h-15" />
                      </svg>
                    </button>
                  )}
                </div>
              ))}
            </div>
            <button
              type="button"
              onClick={() => setGuList((s) => [...s, ''])}
              className="mt-2 text-xs font-medium text-brand-red hover:text-brand-redhover"
            >
              + Add another
            </button>
          </div>

          {/* Transliteration */}
          <div>
            <label className="mb-1.5 block text-xs font-medium text-gray-500">Transliteration</label>
            <div className="space-y-2">
              {trList.map((v, i) => (
                <div key={`tr-${i}`} className="flex gap-2">
                  <input
                    type="text"
                    value={v}
                    onChange={(e) => setTr(i, e.target.value)}
                    placeholder="Transliteration"
                    className={fieldClass}
                  />
                  {trList.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeTr(i)}
                      className="shrink-0 rounded-lg px-2 text-gray-400 transition hover:bg-red-50 hover:text-red-500"
                    >
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 12h-15" />
                      </svg>
                    </button>
                  )}
                </div>
              ))}
            </div>
            <button
              type="button"
              onClick={() => setTrList((s) => [...s, ''])}
              className="mt-2 text-xs font-medium text-brand-red hover:text-brand-redhover"
            >
              + Add another
            </button>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 border-t border-gray-100 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg px-4 py-2.5 text-sm font-medium text-gray-600 transition hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !en.trim()}
              className="rounded-lg bg-brand-red px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-brand-redhover disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? 'Saving...' : isEdit ? 'Save Changes' : 'Add Entry'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
