import { useState } from 'react';
import Card from '../components/common/Card';
import SearchPanel from '../components/common/SearchPanel';
import ResultsTable from '../components/common/ResultsTable';
import StatusAlert from '../components/common/StatusAlert';
import JsonTextarea from '../components/common/JsonTextarea';
import AliasEnGuForm from '../components/forms/AliasEnGuForm';
import DeleteEntryCard from '../components/forms/DeleteEntryCard';
import useApiAction from '../hooks/useApiAction';
import { searchEnGu, patchAliasEnGu, putAliasEnGu, deleteAliasEnGu } from '../services/api';
import { POST_EXAMPLES } from '../constants/postExamples';

function chainPutSnapshot(snapshot, putFn) {
  const entries = Object.entries(snapshot);
  return entries.reduce(
    (p, [canonical_en, gu_aliases]) =>
      p.then(() => {
        const list = Array.isArray(gu_aliases) ? gu_aliases : [String(gu_aliases)];
        return putFn({ entry: { canonical_en, gu_aliases: list } });
      }),
    Promise.resolve(null)
  );
}

export default function AliasesEnGuPage() {
  const [results, setResults] = useState(null);
  const [searchReset, setSearchReset] = useState(0);
  const [formReset, setFormReset] = useState(0);
  const search = useApiAction();
  const action = useApiAction();

  const mutate = (fn) =>
    action.run(fn).then((d) => {
      if (d != null) setFormReset((n) => n + 1);
      return d;
    });

  const handleSearch = (term, limit) => {
    setResults(null);
    return search.run(() => searchEnGu(term, limit)).then((d) => {
      if (d != null) {
        setResults(d);
        setSearchReset((n) => n + 1);
      }
    });
  };

  const handleJsonSubmit = (body) =>
    mutate(() => {
      if (body.entry) return putAliasEnGu(body);
      if (body.snapshot && typeof body.snapshot === 'object') {
        return chainPutSnapshot(body.snapshot, putAliasEnGu);
      }
      return Promise.reject(new Error('JSON must include { entry } or { snapshot }'));
    });

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <StatusAlert {...search.status} onClose={search.clear} />

      <Card>
        <SearchPanel
          onSearch={handleSearch}
          onViewAll={(limit) => handleSearch('', limit)}
          onClear={() => setResults(null)}
          loading={search.loading}
          searchPlaceholder="Search canonical English or Gujarati alias..."
          resetVersion={searchReset}
        />
      </Card>

      <Card>
        <ResultsTable data={results} />
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="flex flex-col">
          <AliasEnGuForm
            onPatch={(b) => mutate(() => patchAliasEnGu(b))}
            onPut={(b) => mutate(() => putAliasEnGu(b))}
            loading={action.loading}
            resetVersion={formReset}
          />
        </Card>
        <Card className="flex flex-col">
          <JsonTextarea
            title="POST / PUT — Bulk from JSON"
            subtitle="Use { entry } for one replace, or { snapshot } to run PUT per canonical key."
            onSubmit={handleJsonSubmit}
            loading={action.loading}
            buttonLabel="Apply JSON (PUT)"
            example={POST_EXAMPLES.aliasesEnGu}
            resetVersion={formReset}
          />
        </Card>
      </div>

      <Card>
        <DeleteEntryCard
          onDelete={(b) => mutate(() => deleteAliasEnGu(b))}
          loading={action.loading}
          placeholder="Enter canonical term to delete (e.g. udder)"
          resetVersion={formReset}
        />
      </Card>

      <StatusAlert {...action.status} onClose={action.clear} />
    </div>
  );
}
