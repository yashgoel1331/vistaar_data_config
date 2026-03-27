import { useState } from 'react';
import PageHeader from '../components/common/PageHeader';
import SearchBar from '../components/common/SearchBar';
import ResultsTable from '../components/common/ResultsTable';
import StatusAlert from '../components/common/StatusAlert';
import KeyValuePatchForm from '../components/forms/KeyValuePatchForm';
import JsonTextarea from '../components/common/JsonTextarea';
import useApiAction from '../hooks/useApiAction';
import { searchGlossary, postGlossary, patchGlossary, deleteGlossary } from '../services/api';

export default function GlossaryPage() {
  const [results, setResults] = useState(null);
  const search = useApiAction();
  const action = useApiAction();

  const handleSearch = (term, limit) =>
    search.run(() => searchGlossary(term, limit)).then((d) => d && setResults(d));

  const handlePost = (body) => action.run(() => postGlossary(body));
  const handlePatch = (body) => action.run(() => patchGlossary(body));
  const handleDelete = (body) => action.run(() => deleteGlossary(body));
  const postExample = `{
  "snapshot": {
    "milk": {
      "gu": ["દૂધ"],
      "transliteration": ["dudh"]
    }
  }
}`;

  return (
    <div>
      <PageHeader title="Glossary" subtitle="glossary_terms — dict of en → {gu, transliteration}" />

      <SearchBar onSearch={handleSearch} loading={search.loading} />
      <StatusAlert {...search.status} onClose={search.clear} />
      <ResultsTable data={results} />

      <div className="grid md:grid-cols-2 gap-4 mt-6">
        <KeyValuePatchForm title="Edit / Delete glossary key" onPatch={handlePatch} onDelete={handleDelete} loading={action.loading} />
        <JsonTextarea
          label="Full snapshot POST"
          onSubmit={handlePost}
          loading={action.loading}
          buttonLabel="POST snapshot"
          example={postExample}
        />
      </div>
      <StatusAlert {...action.status} onClose={action.clear} />
    </div>
  );
}
