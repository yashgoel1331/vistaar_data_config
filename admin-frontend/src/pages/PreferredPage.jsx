import { useState } from 'react';
import Card from '../components/common/Card';
import SearchPanel from '../components/common/SearchPanel';
import ResultsTable from '../components/common/ResultsTable';
import StatusAlert from '../components/common/StatusAlert';
import JsonTextarea from '../components/common/JsonTextarea';
import KeyValuePatchForm from '../components/forms/KeyValuePatchForm';
import DeleteEntryCard from '../components/forms/DeleteEntryCard';
import useApiAction from '../hooks/useApiAction';
import { searchPreferred, postPreferred, patchPreferred, deletePreferred } from '../services/api';
import { POST_EXAMPLES } from '../constants/postExamples';

export default function PreferredPage() {
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
    return search.run(() => searchPreferred(term, limit)).then((d) => {
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
          searchPlaceholder="Search English or Gujarati preferred term..."
          resetVersion={searchReset}
        />
      </Card>

      <Card>
        <ResultsTable data={results} />
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="flex flex-col">
          <KeyValuePatchForm
            onPatch={(b) => mutate(() => patchPreferred(b))}
            loading={action.loading}
            keyLabel="English key"
            valueLabel="Gujarati value"
            valuePlaceholder="Preferred Gujarati text"
            resetVersion={formReset}
          />
        </Card>
        <Card className="flex flex-col">
          <JsonTextarea
            onSubmit={(b) => mutate(() => postPreferred(b))}
            loading={action.loading}
            buttonLabel="POST"
            example={POST_EXAMPLES.preferred}
            resetVersion={formReset}
          />
        </Card>
      </div>

      <Card>
        <DeleteEntryCard
          onDelete={(b) => mutate(() => deletePreferred(b))}
          loading={action.loading}
          placeholder="Enter English key to delete"
          resetVersion={formReset}
        />
      </Card>

      <StatusAlert {...action.status} onClose={action.clear} />
    </div>
  );
}
