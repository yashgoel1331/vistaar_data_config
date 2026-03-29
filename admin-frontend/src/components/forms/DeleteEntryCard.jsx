import { useState, useEffect } from 'react';
import { IconTrash } from '../icons/Icons';

const fieldClass =
  'w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm text-gray-900 placeholder:text-gray-400 focus:border-brand-red focus:outline-none focus:ring-1 focus:ring-brand-red';

export default function DeleteEntryCard({
  onDelete,
  loading,
  title = 'DELETE — Remove Entry',
  description = 'This action is permanent and cannot be undone.',
  keyLabel = 'Key / Identifier',
  placeholder = 'Enter key to delete',
  resetVersion = 0,
}) {
  const [key, setKey] = useState('');

  useEffect(() => {
    if (resetVersion === 0) return;
    setKey('');
  }, [resetVersion]);

  const submit = async (e) => {
    e.preventDefault();
    if (!key.trim()) return;
    await Promise.resolve(onDelete({ entry: { key: key.trim() } }));
  };

  return (
    <div>
      <h3 className="text-base font-semibold text-brand-red">{title}</h3>
      <p className="mt-1 text-sm text-gray-500">{description}</p>
      <form onSubmit={submit} className="mt-4 space-y-4">
        <div>
          <label className="mb-1.5 block text-xs font-medium text-gray-500">{keyLabel}</label>
          <input
            type="text"
            value={key}
            onChange={(e) => setKey(e.target.value)}
            placeholder={placeholder}
            className={fieldClass}
          />
        </div>
        <button
          type="submit"
          disabled={loading || !key.trim()}
          className="inline-flex items-center gap-2 rounded-lg bg-red-100 px-4 py-2.5 text-sm font-medium text-brand-red transition hover:bg-red-200 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <IconTrash />
          {loading ? 'Deleting...' : 'DELETE'}
        </button>
      </form>
    </div>
  );
}
