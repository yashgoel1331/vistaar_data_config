import { useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import SearchBar from '../components/common/SearchBar';
import ResultsTable from '../components/common/ResultsTable';
import StatusAlert from '../components/common/StatusAlert';
import AliasEnglishForm from '../components/forms/AliasEnglishForm';
import useApiAction from '../hooks/useApiAction';
import { searchEnglish, patchAliasEnglish, putAliasEnglish, deleteAliasEnglish } from '../services/api';

export default function AliasesEnglishPage() {
  const [results, setResults] = useState(null);
  const search = useApiAction();
  const action = useApiAction();

  const handleSearch = (term, limit) =>
    search.run(() => searchEnglish(term, limit)).then((d) => d && setResults(d));

  return (
    <div>
      <PageHeader title="Aliases (english)" subtitle="english_aliases — dict of canonical → [aliases]" />

      <SearchBar onSearch={handleSearch} loading={search.loading} />
      <StatusAlert {...search.status} onClose={search.clear} />
      <ResultsTable data={results} />

      <div className="mt-6 max-w-xl">
        <AliasEnglishForm
          onPatch={(b) => action.run(() => patchAliasEnglish(b))}
          onPut={(b) => action.run(() => putAliasEnglish(b))}
          onDelete={(b) => action.run(() => deleteAliasEnglish(b))}
          loading={action.loading}
        />
      </div>
      <StatusAlert {...action.status} onClose={action.clear} />
    </div>
  );
}
