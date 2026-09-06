import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import { searchMaterials } from '../api';
import type { Material } from '../types';

const SearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const [results, setResults] = useState<Material[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (query) {
      setLoading(true);
      searchMaterials(query)
        .then(res => setResults(res.data.items || []))
        .catch(err => console.error(err))
        .finally(() => setLoading(false));
    } else {
      setResults([]);
    }
  }, [query]);

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const q = formData.get('q') as string;
    setSearchParams({ q });
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto pt-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Global Material Search</h1>
        <form onSubmit={handleSearch} className="max-w-2xl mx-auto relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search className="h-6 w-6 text-gray-400" />
          </div>
          <input
            name="q"
            defaultValue={query}
            type="text"
            placeholder="Search by description, CPSE, attributes, or material code..."
            className="block w-full pl-12 pr-4 py-4 border-2 border-gray-200 rounded-xl leading-5 bg-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-0 text-lg shadow-sm transition-colors"
          />
          <button type="submit" className="absolute inset-y-2 right-2 px-6 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors">
            Search
          </button>
        </form>
      </div>

      {loading ? (
        <div className="flex justify-center p-12">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-700"></div>
        </div>
      ) : query && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
            <h2 className="text-sm font-medium text-gray-700">Found {results.length} results for "{query}"</h2>
          </div>
          
          {results.length > 0 ? (
            <div className="divide-y divide-gray-100">
              {results.map(m => (
                <div 
                  key={m.id} 
                  className="p-6 hover:bg-blue-50 cursor-pointer transition-colors"
                  onClick={() => navigate(`/materials/${m.id}`)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-lg font-bold text-blue-700">{m.material_code}</span>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
                        {m.cpse}
                      </span>
                    </div>
                  </div>
                  <p className="text-gray-800 mb-3">{m.description}</p>
                  <div className="flex gap-4 text-sm text-gray-500">
                    {m.category && <span>Category: {m.category}</span>}
                    {m.unit && <span>Unit: {m.unit}</span>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-16 text-center">
              <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-1">No materials found</h3>
              <p className="text-gray-500">Try adjusting your search terms or using broader keywords.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchPage;
