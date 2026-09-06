// pages/standards-explorer.tsx
import React, { useState, useEffect } from 'react';
import { EmptyState } from '../components/EmptyState';
import { Layout } from '../components/Layout';

export default function StandardsExplorer() {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [selectedStandard, setSelectedStandard] = useState<any>(null);

  useEffect(() => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }
    const delayDebounceFn = setTimeout(async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/explorer/standards?query=${encodeURIComponent(searchQuery)}`);
        const data = await res.json();
        setResults(data);
      } catch (err) {
        console.error(err);
      }
    }, 300);
    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery]);

  const selectStandard = async (id: number) => {
    try {
      const res = await fetch(`http://localhost:8000/api/explorer/standards/${id}`);
      const data = await res.json();
      setSelectedStandard(data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <Layout>
      <div className="flex h-full border-t border-gray-300">
        {/* Left Search Pane */}
        <div className="w-1/3 min-w-[300px] border-r border-gray-300 bg-gray-50 flex flex-col">
          <div className="p-4 border-b border-gray-300 bg-white">
            <h1 className="text-lg font-bold text-gray-900 mb-3">Standards Library</h1>
            <input
              type="text"
              className="w-full p-2.5 border border-gray-300 text-sm focus:border-blue-600 focus:ring-1 focus:ring-blue-600 outline-none"
              placeholder="Search IS number, title, or keyword..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-2">
             {results.length === 0 ? (
               <div className="text-center text-sm text-gray-500 mt-10">
                  Search results will populate here.
               </div>
             ) : (
               results.map(r => (
                 <div 
                    key={r.id} 
                    onClick={() => selectStandard(r.id)}
                    className="p-3 bg-white border border-gray-200 cursor-pointer hover:border-blue-500"
                  >
                   <div className="font-bold text-sm text-blue-800">{r.number}</div>
                   <div className="text-xs text-gray-600 line-clamp-2">{r.title}</div>
                 </div>
               ))
             )}
          </div>
        </div>
        
        {/* Right Details Pane */}
        <div className="flex-1 bg-white p-8 overflow-y-auto">
          {!selectedStandard ? (
            <EmptyState
              title="No Standard Selected"
              description="Select a standard from the search panel to view authoritative clauses, testing requirements, and scheme relations."
            />
          ) : (
            <div>
              <h2 className="text-2xl font-bold mb-2">{selectedStandard.number}</h2>
              <p className="text-lg text-gray-700 mb-6">{selectedStandard.title}</p>
              
              <div className="mb-6">
                <h3 className="font-semibold text-gray-800 border-b pb-2 mb-3">Status</h3>
                <span className="bg-green-100 text-green-800 px-2 py-1 text-xs font-bold uppercase">{selectedStandard.status}</span>
              </div>
              
              <div className="mb-6">
                <h3 className="font-semibold text-gray-800 border-b pb-2 mb-3">Testing Information</h3>
                <p className="text-sm text-gray-600">{selectedStandard.testing_information}</p>
              </div>

              <div className="mb-6">
                <h3 className="font-semibold text-gray-800 border-b pb-2 mb-3">Clauses</h3>
                <div className="space-y-4">
                  {selectedStandard.clauses?.map((c: any) => (
                    <div key={c.id} className="p-4 bg-gray-50 border border-gray-200">
                      <div className="font-bold text-sm text-gray-800 mb-2">Clause {c.clause_number}</div>
                      <p className="text-sm text-gray-600">{c.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
