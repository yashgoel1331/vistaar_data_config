import { useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import SearchBar from '../components/common/SearchBar';
import ResultsTable from '../components/common/ResultsTable';
import StatusAlert from '../components/common/StatusAlert';
import KeyValuePatchForm from '../components/forms/KeyValuePatchForm';
import JsonTextarea from '../components/common/JsonTextarea';
import useApiAction from '../hooks/useApiAction';
import { searchSchemes, postSchemes, patchSchemes, deleteSchemes } from '../services/api';

export default function SchemesPage() {
  const [results, setResults] = useState(null);
  const search = useApiAction();
  const action = useApiAction();

  const handleSearch = (term, limit) =>
    search.run(() => searchSchemes(term, limit)).then((d) => d && setResults(d));
  const postExample = `{
  "snapshot": {
    "aif": "Agriculture Infrastructure Fund (AIF)",
    "bksy": "Dr. Babasaheb Ambedkar Krushi Swavalamban Yojna",
    "agroforestry": "Nanaji Deshmukh Krishi Sanjivani Prakalp Agroforestry"
  },
  "note": "updated schemes list"
}`;

  return (
    <div>
      <PageHeader title="Schemes" subtitle="schemes — dict of abbreviation → full_name" />

      <SearchBar onSearch={handleSearch} loading={search.loading} />
      <StatusAlert {...search.status} onClose={search.clear} />
      <ResultsTable data={results} />

      <div className="grid md:grid-cols-2 gap-4 mt-6">
        <KeyValuePatchForm title="Edit / Delete schemes key" onPatch={(b) => action.run(() => patchSchemes(b))} onDelete={(b) => action.run(() => deleteSchemes(b))} loading={action.loading} />
        <JsonTextarea
          label="Full snapshot POST"
          onSubmit={(b) => action.run(() => postSchemes(b))}
          loading={action.loading}
          buttonLabel="POST snapshot"
          example={postExample}
        />
      </div>
      <StatusAlert {...action.status} onClose={action.clear} />
    </div>
  );
}
