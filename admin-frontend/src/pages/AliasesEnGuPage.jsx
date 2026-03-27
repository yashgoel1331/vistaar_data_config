import { useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import SearchBar from '../components/common/SearchBar';
import ResultsTable from '../components/common/ResultsTable';
import StatusAlert from '../components/common/StatusAlert';
import AliasEnGuForm from '../components/forms/AliasEnGuForm';
import useApiAction from '../hooks/useApiAction';
import { searchEnGu, patchAliasEnGu, putAliasEnGu, deleteAliasEnGu } from '../services/api';

export default function AliasesEnGuPage() {
  const [results, setResults] = useState(null);
  const search = useApiAction();
  const action = useApiAction();

  const handleSearch = (term, limit) =>
    search.run(() => searchEnGu(term, limit)).then((d) => d && setResults(d));

  return (
    <div>
      <PageHeader title="Aliases (en-gu)" subtitle="en-gujarati_aliases — dict of canonical → [gu aliases]" />

      <SearchBar onSearch={handleSearch} loading={search.loading} />
      <StatusAlert {...search.status} onClose={search.clear} />
      <ResultsTable data={results} />

      <div className="mt-6 max-w-xl">
        <AliasEnGuForm
          onPatch={(b) => action.run(() => patchAliasEnGu(b))}
          onPut={(b) => action.run(() => putAliasEnGu(b))}
          onDelete={(b) => action.run(() => deleteAliasEnGu(b))}
          loading={action.loading}
        />
      </div>
      <StatusAlert {...action.status} onClose={action.clear} />
    </div>
  );
}
