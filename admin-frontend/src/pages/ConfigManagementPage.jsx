import { useState, useEffect } from 'react';
import Card from '../components/common/Card';
import StatusAlert from '../components/common/StatusAlert';
import useApiAction from '../hooks/useApiAction';
import { reloadConfigs, rollbackConfig, getVersions } from '../services/api';
import { CONFIG_TYPE_OPTIONS } from '../constants/nav';
import { IconRefresh, IconRollback, IconAlert } from '../components/icons/Icons';

export default function ConfigManagementPage() {
  const reload = useApiAction();
  const rollback = useApiAction();
  const versions = useApiAction();

  const [selectedType, setSelectedType] = useState(CONFIG_TYPE_OPTIONS[0].value);
  const [rollbackVersion, setRollbackVersion] = useState('');
  const [versionList, setVersionList] = useState([]);
  const [formReset, setFormReset] = useState(0);

  useEffect(() => {
    if (formReset === 0) return;
    setRollbackVersion('');
  }, [formReset]);

  const bumpOnSuccess = (d) => {
    if (d != null) setFormReset((n) => n + 1);
    return d;
  };

  const handleReload = () => reload.run(() => reloadConfigs()).then(bumpOnSuccess);

  const handleRollback = (e) => {
    e.preventDefault();
    const ver = parseInt(rollbackVersion, 10);
    if (!ver || ver <= 0) return;
    rollback
      .run(() => rollbackConfig({ config_type: selectedType, version: ver }))
      .then(bumpOnSuccess);
  };

  const handleQuickRollback = (ver) => {
    rollback
      .run(() => rollbackConfig({ config_type: selectedType, version: ver }))
      .then(bumpOnSuccess);
  };

  const handleFetchVersions = () => {
    versions.run(() => getVersions(selectedType)).then((d) => {
      if (d?.versions) setVersionList(d.versions);
    });
  };

  const fieldClass =
    'w-full rounded-lg border border-gray-200 px-3 py-2.5 text-sm text-gray-900 focus:border-brand-red focus:outline-none focus:ring-1 focus:ring-brand-red';

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Card>
        <h2 className="text-lg font-semibold text-gray-900">Reload Configs</h2>
        <p className="mt-2 text-sm text-gray-500">
          Force reload all configuration from the latest saved state in the database. This refreshes in-memory caches.
        </p>
        <button
          type="button"
          onClick={handleReload}
          disabled={reload.loading}
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-brand-red px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-brand-redhover disabled:cursor-not-allowed disabled:opacity-50"
        >
          <IconRefresh />
          {reload.loading ? 'Reloading...' : 'Reload All Configs'}
        </button>
        <div className="mt-4">
          <StatusAlert {...reload.status} onClose={reload.clear} />
        </div>
      </Card>

      <Card>
        <h2 className="text-lg font-semibold text-gray-900">Rollback Config</h2>
        <div className="mt-3 flex items-start gap-2 text-sm text-brand-red">
          <IconAlert className="mt-0.5 h-5 w-5 shrink-0" />
          <span>This action will create a new version from a historical snapshot.</span>
        </div>

        <form onSubmit={handleRollback} className="mt-6 space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-gray-500">Config Type</label>
              <select
                value={selectedType}
                onChange={(e) => {
                  setSelectedType(e.target.value);
                  setVersionList([]);
                }}
                className={fieldClass}
              >
                {CONFIG_TYPE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-gray-500">Version</label>
              <input
                type="number"
                min="1"
                value={rollbackVersion}
                onChange={(e) => setRollbackVersion(e.target.value)}
                className={fieldClass}
                placeholder="Enter version number (e.g. 8)"
              />
              <p className="mt-1.5 text-xs text-gray-500">Restores that snapshot as a new latest version.</p>
            </div>
          </div>
          <button
            type="submit"
            disabled={rollback.loading || !rollbackVersion}
            className="inline-flex items-center gap-2 rounded-lg bg-red-100 px-4 py-2.5 text-sm font-medium text-brand-red transition hover:bg-red-200 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <IconRollback />
            {rollback.loading ? 'Rolling back...' : 'Rollback'}
          </button>
        </form>
        <div className="mt-4">
          <StatusAlert {...rollback.status} onClose={rollback.clear} />
        </div>
      </Card>

      <Card>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Version history</h2>
          <button
            type="button"
            onClick={handleFetchVersions}
            disabled={versions.loading}
            className="inline-flex rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-800 shadow-sm hover:bg-gray-50 disabled:opacity-50"
          >
            {versions.loading ? 'Loading...' : 'Load versions'}
          </button>
        </div>
        <div className="mt-4">
          <StatusAlert {...versions.status} onClose={versions.clear} />
        </div>

        {versionList.length > 0 && (
          <div className="mt-4 overflow-x-auto rounded-lg border border-gray-200">
            <table className="w-full min-w-[480px] text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-600">
                    Version
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-600">
                    Triggered by
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-600">
                    Note
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-600">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {versionList.map((v) => (
                  <tr key={v.version_number} className="hover:bg-gray-50/80">
                    <td className="px-4 py-3 font-mono text-gray-900">{v.version_number}</td>
                    <td className="px-4 py-3 text-gray-700">{v.triggered_by || '—'}</td>
                    <td className="px-4 py-3 text-gray-600" title={v.note}>
                      {v.note || '—'}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        type="button"
                        onClick={() => handleQuickRollback(v.version_number)}
                        disabled={rollback.loading}
                        className="rounded-lg bg-brand-mustard px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-mustardhover disabled:opacity-50"
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
      </Card>
    </div>
  );
}
