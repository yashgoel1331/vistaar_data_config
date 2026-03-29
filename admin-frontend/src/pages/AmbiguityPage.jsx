import { useState } from 'react';
import Card from '../components/common/Card';
import SearchPanel from '../components/common/SearchPanel';
import ResultsTable from '../components/common/ResultsTable';
import StatusAlert from '../components/common/StatusAlert';
import JsonTextarea from '../components/common/JsonTextarea';
import AmbiguityPatchForm from '../components/forms/AmbiguityPatchForm';
import useApiAction from '../hooks/useApiAction';
import { searchAmbiguousTerms, patchAmbiguousTerms } from '../services/api';
import { POST_EXAMPLES } from '../constants/postExamples';

export default function AmbiguityPage() {
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
    return search.run(() => searchAmbiguousTerms(term, limit)).then((d) => {
      if (d != null) {
        setResults(d);
        setSearchReset((n) => n + 1);
      }
    });
  };

  const handleJsonSubmit = (body) =>
    mutate(() => {
      if (body.entry) return patchAmbiguousTerms(body);
      if (Array.isArray(body.snapshot)) {
        return body.snapshot.reduce(
          (p, row) => p.then(() => patchAmbiguousTerms({ entry: row })),
          Promise.resolve(null)
        );
      }
      return Promise.reject(new Error('JSON must include { entry } or { snapshot: [...] }'));
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
          searchPlaceholder="Search Gujarati terms or rule text..."
          resetVersion={searchReset}
        />
      </Card>

      <Card>
        <ResultsTable data={results} />
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="flex flex-col">
          <AmbiguityPatchForm
            onSubmit={(b) => mutate(() => patchAmbiguousTerms(b))}
            loading={action.loading}
            resetVersion={formReset}
          />
        </Card>
        <Card className="flex flex-col">
          <JsonTextarea
            onSubmit={handleJsonSubmit}
            loading={action.loading}
            buttonLabel="Apply JSON (PATCH)"
            example={POST_EXAMPLES.ambiguousTerms}
            resetVersion={formReset}
          />
        </Card>
      </div>

      <StatusAlert {...action.status} onClose={action.clear} />
    </div>
  );
}
