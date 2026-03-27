import { useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import StatusAlert from '../components/common/StatusAlert';
import useApiAction from '../hooks/useApiAction';
import { reloadConfigs, rollbackConfig, getVersions } from '../services/api';
import { CONFIG_TYPE_OPTIONS } from '../constants/nav';

export default function ConfigManagementPage() {
  const reload = useApiAction();
  const rollback = useApiAction();
  const versions = useApiAction();

  const [selectedType, setSelectedType] = useState(CONFIG_TYPE_OPTIONS[0].value);
  const [rollbackVersion, setRollbackVersion] = useState('');
  const [versionList, setVersionList] = useState([]);

  const handleReload = () => reload.run(() => reloadConfigs());

  const handleRollback = (e) => {
    e.preventDefault();
    const ver = parseInt(rollbackVersion, 10);
    if (!ver || ver <= 0) return;
    rollback.run(() => rollbackConfig({ config_type: selectedType, version: ver }));
  };

  const handleQuickRollback = (ver) => {
    rollback.run(() => rollbackConfig({ config_type: selectedType, version: ver }));
  };

  const handleFetchVersions = () => {
    versions.run(() => getVersions(selectedType)).then((d) => {
      if (d?.versions) setVersionList(d.versions);
    });
  };

  return (
    <div>
      <PageHeader title="Config Management" subtitle="Reload, rollback, and view version history" />

      {/* Reload */}
      <section className="mb-8 p-4 border rounded bg-white">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Reload all configs</h2>
        <button
          onClick={handleReload}
          disabled={reload.loading}
          className="px-4 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
        >
          {reload.loading ? 'Reloading...' : 'POST /configs/reload'}
        </button>
        <StatusAlert {...reload.status} onClose={reload.clear} />
      </section>

      {/* Config type selector (shared between rollback + versions) */}
      <section className="mb-4">
        <label className="block text-xs font-medium text-gray-500 mb-1">Config type</label>
        <select
          value={selectedType}
          onChange={(e) => { setSelectedType(e.target.value); setVersionList([]); }}
          className="border rounded px-3 py-2 text-sm w-64"
        >
          {CONFIG_TYPE_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </section>

      {/* Rollback */}
      <section className="mb-8 p-4 border rounded bg-white">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Rollback</h2>
        <form onSubmit={handleRollback} className="flex gap-2 items-end">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Version number</label>
            <input
              type="number"
              min="1"
              value={rollbackVersion}
              onChange={(e) => setRollbackVersion(e.target.value)}
              className="border rounded px-3 py-2 text-sm w-32"
              placeholder="e.g. 8"
            />
          </div>
          <button
            type="submit"
            disabled={rollback.loading || !rollbackVersion}
            className="px-4 py-2 text-sm bg-amber-600 text-white rounded hover:bg-amber-700 disabled:opacity-50"
          >
            {rollback.loading ? 'Rolling back...' : 'Rollback'}
          </button>
        </form>
        <StatusAlert {...rollback.status} onClose={rollback.clear} />
      </section>

      {/* Version history */}
      <section className="p-4 border rounded bg-white">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-gray-700">Version history</h2>
          <button
            onClick={handleFetchVersions}
            disabled={versions.loading}
            className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
          >
            {versions.loading ? 'Loading...' : 'Load versions'}
          </button>
        </div>
        <StatusAlert {...versions.status} onClose={versions.clear} />

        {versionList.length > 0 && (
          <div className="overflow-x-auto border rounded max-h-96 overflow-y-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-gray-100 sticky top-0">
                <tr>
                  <th className="px-3 py-2 font-medium text-gray-600 border-b">Version</th>
                  <th className="px-3 py-2 font-medium text-gray-600 border-b">Triggered by</th>
                  <th className="px-3 py-2 font-medium text-gray-600 border-b">Note</th>
                  <th className="px-3 py-2 font-medium text-gray-600 border-b">Action</th>
                </tr>
              </thead>
              <tbody>
                {versionList.map((v) => (
                  <tr key={v.version_number} className="border-b hover:bg-gray-50">
                    <td className="px-3 py-2 font-mono">{v.version_number}</td>
                    <td className="px-3 py-2">{v.triggered_by || '—'}</td>
                    <td className="px-3 py-2 max-w-xs truncate" title={v.note}>{v.note || '—'}</td>
                    <td className="px-3 py-2">
                      <button
                        onClick={() => handleQuickRollback(v.version_number)}
                        disabled={rollback.loading}
                        className="text-xs px-2 py-1 bg-amber-100 text-amber-800 rounded hover:bg-amber-200 disabled:opacity-50"
                      >
                        Rollback to this
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
