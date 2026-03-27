import { useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import SearchBar from '../components/common/SearchBar';
import ResultsTable from '../components/common/ResultsTable';
import StatusAlert from '../components/common/StatusAlert';
import AmbiguityPatchForm from '../components/forms/AmbiguityPatchForm';
import useApiAction from '../hooks/useApiAction';
import { searchAmbiguousTerms, patchAmbiguousTerms } from '../services/api';

export default function AmbiguityPage() {
  const [results, setResults] = useState(null);
  const search = useApiAction();
  const action = useApiAction();

  const handleSearch = (term, limit) =>
    search.run(() => searchAmbiguousTerms(term, limit)).then((d) => d && setResults(d));

  const handlePatch = (body) => action.run(() => patchAmbiguousTerms(body));

  return (
    <div>
      <PageHeader title="Ambiguous Terms" subtitle="ambiguous_terms — list of rule objects" />

      <SearchBar onSearch={handleSearch} loading={search.loading} />
      <StatusAlert {...search.status} onClose={search.clear} />
      <ResultsTable data={results} />

      <div className="mt-6 max-w-xl">
        <AmbiguityPatchForm onSubmit={handlePatch} loading={action.loading} />
      </div>
      <StatusAlert {...action.status} onClose={action.clear} />
    </div>
  );
}
