import { useState, useEffect } from 'react';

const fieldClass =
  'w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:border-brand-red focus:outline-none focus:ring-1 focus:ring-brand-red';

export default function KeyValuePatchForm({
  onPatch,
  loading,
  keyLabel = 'Key',
  valueLabel = 'Value',
  keyPlaceholder = 'Enter key',
  valuePlaceholder = 'Enter value (string or JSON)',
  patchSubtitle = 'Use POST to add new entries. PATCH updates existing ones.',
  resetVersion = 0,
}) {
  const [key, setKey] = useState('');
  const [value, setValue] = useState('');

  useEffect(() => {
    if (resetVersion === 0) return;
    setKey('');
    setValue('');
  }, [resetVersion]);

  const handlePatch = async (e) => {
    e.preventDefault();
    if (!key.trim()) return;
    let parsed = value;
    try {
      parsed = JSON.parse(value);
    } catch {
      /* keep as string */
    }
    await Promise.resolve(onPatch({ entry: { key: key.trim(), value: parsed } }));
  };

  return (
    <form onSubmit={handlePatch} className="flex h-full flex-col">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-gray-900">PATCH — Update Existing Entry</h3>
        <p className="mt-1 text-sm text-gray-500">{patchSubtitle}</p>
      </div>
      <div className="space-y-4">
        <div>
          <label className="mb-1.5 block text-xs font-medium text-gray-500">{keyLabel}</label>
          <input
            type="text"
            value={key}
            onChange={(e) => setKey(e.target.value)}
            placeholder={keyPlaceholder}
            className={fieldClass}
          />
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-medium text-gray-500">{valueLabel}</label>
          <textarea
            value={value}
            onChange={(e) => setValue(e.target.value)}
            rows={4}
            placeholder={valuePlaceholder}
            className={fieldClass}
          />
        </div>
      </div>
      <button
        type="submit"
        disabled={loading || !key.trim()}
        className="mt-6 inline-flex w-full justify-center rounded-lg bg-brand-red px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-brand-redhover disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
      >
        {loading ? 'Saving...' : 'PATCH'}
      </button>
    </form>
  );
}
