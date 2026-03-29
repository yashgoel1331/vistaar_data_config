import { useState } from 'react';
import Card from '../components/common/Card';
import SearchPanel from '../components/common/SearchPanel';
import ResultsTable from '../components/common/ResultsTable';
import StatusAlert from '../components/common/StatusAlert';
import JsonTextarea from '../components/common/JsonTextarea';
import GlossaryPatchForm from '../components/forms/GlossaryPatchForm';
import DeleteEntryCard from '../components/forms/DeleteEntryCard';
import useApiAction from '../hooks/useApiAction';
import { searchGlossary, postGlossary, patchGlossary, deleteGlossary } from '../services/api';
import { POST_EXAMPLES } from '../constants/postExamples';

export default function GlossaryPage() {
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
    return search.run(() => searchGlossary(term, limit)).then((d) => {
      if (d != null) {
        setResults(d);
        setSearchReset((n) => n + 1);
      }
    });
  };

  const handleViewAll = (limit) => handleSearch('', limit);

  const handleClear = () => setResults(null);

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <StatusAlert {...search.status} onClose={search.clear} />

      <Card>
        <SearchPanel
          onSearch={handleSearch}
          onViewAll={handleViewAll}
          onClear={handleClear}
          loading={search.loading}
          searchPlaceholder="Search English, Gujarati, or transliteration..."
          resetVersion={searchReset}
        />
      </Card>

      <Card>
        <ResultsTable data={results} />
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="flex flex-col">
          <GlossaryPatchForm
            onPatch={(b) => mutate(() => patchGlossary(b))}
            loading={action.loading}
            resetVersion={formReset}
          />
        </Card>
        <Card className="flex flex-col">
          <JsonTextarea
            onSubmit={(b) => mutate(() => postGlossary(b))}
            loading={action.loading}
            buttonLabel="POST"
            example={POST_EXAMPLES.glossary}
            resetVersion={formReset}
          />
        </Card>
      </div>

      <Card>
        <DeleteEntryCard
          onDelete={(b) => mutate(() => deleteGlossary(b))}
          loading={action.loading}
          placeholder="Enter English term to delete (e.g. milk)"
          resetVersion={formReset}
        />
      </Card>

      <StatusAlert {...action.status} onClose={action.clear} />
    </div>
  );
}
