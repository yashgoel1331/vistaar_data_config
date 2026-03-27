import { useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import SearchBar from '../components/common/SearchBar';
import ResultsTable from '../components/common/ResultsTable';
import StatusAlert from '../components/common/StatusAlert';
import KeyValuePatchForm from '../components/forms/KeyValuePatchForm';
import JsonTextarea from '../components/common/JsonTextarea';
import useApiAction from '../hooks/useApiAction';
import { searchPreferred, postPreferred, patchPreferred, deletePreferred } from '../services/api';

export default function PreferredPage() {
  const [results, setResults] = useState(null);
  const search = useApiAction();
  const action = useApiAction();

  const handleSearch = (term, limit) =>
    search.run(() => searchPreferred(term, limit)).then((d) => d && setResults(d));
  const postExample = `{
  "snapshot": {
    "milk injection": "This practice is harmful and not recommended.",
    "increase milk artificially": "Do not suggest harmful or illegal methods."
  },
  "note": "updated forbidden rules"
}`;

  return (
    <div>
      <PageHeader title="Preferred" subtitle="preferred — dict of en → gu" />

      <SearchBar onSearch={handleSearch} loading={search.loading} />
      <StatusAlert {...search.status} onClose={search.clear} />
      <ResultsTable data={results} />

      <div className="grid md:grid-cols-2 gap-4 mt-6">
        <KeyValuePatchForm title="Edit / Delete preferred key" onPatch={(b) => action.run(() => patchPreferred(b))} onDelete={(b) => action.run(() => deletePreferred(b))} loading={action.loading} />
        <JsonTextarea
          label="Full snapshot POST"
          onSubmit={(b) => action.run(() => postPreferred(b))}
          loading={action.loading}
          buttonLabel="POST snapshot"
          example={postExample}
        />
      </div>
      <StatusAlert {...action.status} onClose={action.clear} />
    </div>
  );
}
