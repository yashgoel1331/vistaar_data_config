import { useState } from 'react';
import Card from '../components/common/Card';
import SearchPanel from '../components/common/SearchPanel';
import ResultsTable from '../components/common/ResultsTable';
import StatusAlert from '../components/common/StatusAlert';
import JsonTextarea from '../components/common/JsonTextarea';
import KeyValuePatchForm from '../components/forms/KeyValuePatchForm';
import DeleteEntryCard from '../components/forms/DeleteEntryCard';
import useApiAction from '../hooks/useApiAction';
import { searchSchemes, postSchemes, patchSchemes, deleteSchemes } from '../services/api';
import { POST_EXAMPLES } from '../constants/postExamples';

export default function SchemesPage() {
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
    return search.run(() => searchSchemes(term, limit)).then((d) => {
      if (d != null) {
        setResults(d);
        setSearchReset((n) => n + 1);
      }
    });
  };

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <StatusAlert {...search.status} onClose={search.clear} />

      <Card>
        <SearchPanel
          onSearch={handleSearch}
          onViewAll={(limit) => handleSearch('', limit)}
          onClear={() => setResults(null)}
          loading={search.loading}
          searchPlaceholder="Search abbreviation or full scheme name..."
          resetVersion={searchReset}
        />
      </Card>

      <Card>
        <ResultsTable data={results} />
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="flex flex-col">
          <KeyValuePatchForm
            onPatch={(b) => mutate(() => patchSchemes(b))}
            loading={action.loading}
            keyLabel="Abbreviation"
            valueLabel="Full name"
            valuePlaceholder="Full scheme name"
            resetVersion={formReset}
          />
        </Card>
        <Card className="flex flex-col">
          <JsonTextarea
            onSubmit={(b) => mutate(() => postSchemes(b))}
            loading={action.loading}
            buttonLabel="POST"
            example={POST_EXAMPLES.schemes}
            resetVersion={formReset}
          />
        </Card>
      </div>

      <Card>
        <DeleteEntryCard
          onDelete={(b) => mutate(() => deleteSchemes(b))}
          loading={action.loading}
          placeholder="Enter abbreviation to delete"
          resetVersion={formReset}
        />
      </Card>

      <StatusAlert {...action.status} onClose={action.clear} />
    </div>
  );
}
