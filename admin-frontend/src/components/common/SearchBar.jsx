import { useState } from 'react';

export default function SearchBar({ onSearch, loading }) {
  const [term, setTerm] = useState('');
  const [limit, setLimit] = useState('20');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(term.trim(), limit.trim() || undefined);
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 items-end mb-4">
      <div className="flex-1">
        <label className="block text-xs font-medium text-gray-500 mb-1">Search term</label>
        <input
          value={term}
          onChange={(e) => setTerm(e.target.value)}
          placeholder="Enter search term..."
          className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
      </div>
      <div className="w-24">
        <label className="block text-xs font-medium text-gray-500 mb-1">Limit</label>
        <input
          value={limit}
          onChange={(e) => setLimit(e.target.value)}
          placeholder="20"
          className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="px-4 py-2 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Searching...' : 'Search'}
      </button>
    </form>
  );
}
