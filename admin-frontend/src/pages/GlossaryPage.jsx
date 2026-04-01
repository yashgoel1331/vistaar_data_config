import { useState } from 'react';
import Card from '../components/common/Card';
import SearchPanel from '../components/common/SearchPanel';
import GlossaryCards from '../components/common/GlossaryCards';
import GlossaryModal from '../components/common/GlossaryModal';
import StatusAlert from '../components/common/StatusAlert';
import useApiAction from '../hooks/useApiAction';
import { searchGlossary, postGlossary, patchGlossary, deleteGlossary } from '../services/api';

export default function GlossaryPage() {
  const [results, setResults] = useState(null);
  const [lastSearch, setLastSearch] = useState({ term: '', limit: undefined });

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(null);

  const search = useApiAction();
  const action = useApiAction();

  const doSearch = (term, limit) => {
    setLastSearch({ term, limit });
    setResults(null);
    search.clear();
    return search.run(() => searchGlossary(term, limit)).then((d) => {
      if (d != null) setResults(d);
    });
  };

  const refresh = () => doSearch(lastSearch.term, lastSearch.limit);

  const handleAdd = () => {
    setEditTarget(null);
    setModalOpen(true);
  };

  const handleEdit = (row) => {
    setEditTarget(row);
    setModalOpen(true);
  };

  const handleModalSubmit = async (body) => {
    const fn = editTarget ? () => patchGlossary(body) : () => postGlossary(body);
    const d = await action.run(fn);
    if (d != null) {
      setModalOpen(false);
      setEditTarget(null);
      refresh();
    }
  };

  const handleDeleteClick = (term) => {
    setConfirmDelete(term);
  };

  const handleDeleteConfirm = async () => {
    if (!confirmDelete) return;
    const d = await action.run(() => deleteGlossary({ entry: { key: confirmDelete } }));
    if (d != null) {
      setConfirmDelete(null);
      refresh();
    }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      {/* Only show errors, not success JSON dumps */}
      {search.status?.type === 'error' && (
        <StatusAlert {...search.status} onClose={search.clear} />
      )}
      {action.status && (
        <StatusAlert
          type={action.status.type}
          message={action.status.type === 'success' ? 'Done.' : action.status.message}
          onClose={action.clear}
        />
      )}

      {/* Search bar row with Add button aligned */}
      <Card>
        <SearchPanel
          onSearch={doSearch}
          onViewAll={(limit) => doSearch('', limit)}
          onClear={() => setResults(null)}
          loading={search.loading}
          searchPlaceholder="Search English, Gujarati, or transliteration..."
          extraButtons={
            <button
              onClick={handleAdd}
              className="inline-flex items-center gap-1.5 rounded-lg bg-brand-red px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-brand-redhover"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
              </svg>
              Add Entry
            </button>
          }
        />
      </Card>

      {/* Results */}
      <Card>
        <GlossaryCards
          data={results}
          onEdit={handleEdit}
          onDelete={handleDeleteClick}
          actionLoading={action.loading}
        />
      </Card>

      {/* Add/Edit Modal */}
      <GlossaryModal
        open={modalOpen}
        onClose={() => { setModalOpen(false); setEditTarget(null); }}
        onSubmit={handleModalSubmit}
        loading={action.loading}
        initial={editTarget}
      />

      {/* Delete Confirmation */}
      {confirmDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setConfirmDelete(null)} />
          <div className="relative mx-4 w-full max-w-sm rounded-2xl border border-gray-200 bg-white p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-gray-900">Delete Entry</h3>
            <p className="mt-2 text-sm text-gray-600">
              Are you sure you want to delete <span className="font-semibold text-brand-red">"{confirmDelete}"</span>? This cannot be undone.
            </p>
            <div className="mt-5 flex justify-end gap-3">
              <button
                onClick={() => setConfirmDelete(null)}
                className="rounded-lg px-4 py-2.5 text-sm font-medium text-gray-600 transition hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                disabled={action.loading}
                className="rounded-lg bg-red-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-red-700 disabled:opacity-50"
              >
                {action.loading ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
