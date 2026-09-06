// pages/lab-finder.tsx
import React, { useState } from 'react';
import { Layout } from '../components/Layout';
import { EmptyState } from '../components/EmptyState';

export default function LabFinder() {
  const [productCategory, setProductCategory] = useState('');
  const [standardNumber, setStandardNumber] = useState('');
  const [testType, setTestType] = useState('');
  const [location, setLocation] = useState('');
  
  const [hasSearched, setHasSearched] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async () => {
    setIsLoading(true);
    setHasSearched(true);
    try {
      const res = await fetch('http://localhost:8000/api/labs/discovery/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
           query: productCategory || undefined,
           standard_number: standardNumber || undefined,
           test_type: testType || undefined,
           location: location || undefined
        })
      });
      const data = await res.json();
      setResults(data.results || []);
    } catch (err) {
      console.error(err);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <div className="flex h-full border-t border-gray-300">
        <div className="w-1/3 min-w-[300px] border-r border-gray-300 bg-white flex flex-col h-full overflow-y-auto p-6">
          <h1 className="text-xl font-bold text-gray-900 mb-6">BIS Recognized Labs</h1>
          
          <div className="space-y-5">
            <div>
              <label className="block text-xs font-semibold uppercase text-gray-500 mb-1">Product Category</label>
              <input 
                type="text" 
                className="w-full p-2 border border-gray-300 text-sm focus:border-blue-600 focus:ring-1 outline-none" 
                placeholder="e.g., Electronics, Textiles..." 
                value={productCategory}
                onChange={(e) => setProductCategory(e.target.value)}
              />
            </div>
            
            <div>
              <label className="block text-xs font-semibold uppercase text-gray-500 mb-1">Standard Number</label>
              <input 
                type="text" 
                className="w-full p-2 border border-gray-300 text-sm focus:border-blue-600 focus:ring-1 outline-none" 
                placeholder="e.g., IS 1234" 
                value={standardNumber}
                onChange={(e) => setStandardNumber(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase text-gray-500 mb-1">Test Type</label>
              <input 
                type="text" 
                className="w-full p-2 border border-gray-300 text-sm focus:border-blue-600 focus:ring-1 outline-none" 
                placeholder="e.g., Tensile strength" 
                value={testType}
                onChange={(e) => setTestType(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase text-gray-500 mb-1">Location</label>
              <input 
                type="text" 
                className="w-full p-2 border border-gray-300 text-sm focus:border-blue-600 focus:ring-1 outline-none" 
                placeholder="e.g., Delhi, Mumbai" 
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>

            <button 
              onClick={handleSearch}
              className="w-full bg-blue-700 text-white py-2.5 text-sm font-medium hover:bg-blue-800 transition-colors mt-2"
            >
              Search Laboratories
            </button>
          </div>
        </div>

        <div className="flex-1 bg-gray-50 p-8 overflow-y-auto">
          {!hasSearched ? (
            <EmptyState 
              title="Find Verified Laboratories" 
              description="Enter criteria on the left to securely query the database of BIS recognized and NABL accredited testing facilities." 
            />
          ) : isLoading ? (
            <div className="flex justify-center items-center h-full text-gray-500">Searching...</div>
          ) : results.length === 0 ? (
            <div className="flex justify-center items-center h-full text-gray-500">No verified laboratories found matching these criteria.</div>
          ) : (
            <div>
              <h2 className="text-lg font-bold mb-4">{results.length} Verified Facilities Found</h2>
              <div className="space-y-4">
                {results.map((lab, i) => (
                  <div key={i} className="bg-white border border-gray-300 p-5 shadow-sm">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="text-lg font-bold text-gray-900">{lab.name}</h3>
                        <div className="text-sm text-gray-600 flex items-center gap-2 mt-1">
                          <span className="font-medium text-gray-800">{lab.location}</span>
                          <span>•</span>
                          <span className="bg-blue-100 text-blue-800 px-2 py-0.5 text-xs font-bold">{lab.accreditation}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-4 border-t border-gray-100 pt-3">
                      <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Verified Testing Capabilities</h4>
                      <div className="flex flex-wrap gap-2">
                        {lab.capabilities?.map((cap: any, j: number) => (
                          <span key={j} className="bg-gray-100 text-gray-800 border border-gray-200 px-2 py-1 text-xs">
                            {cap.test_name} {cap.related_standard ? `(${cap.related_standard})` : ''}
                          </span>
                        ))}
                        {!lab.capabilities?.length && <span className="text-xs text-gray-500">No specific tests listed</span>}
                      </div>
                    </div>

                    <div className="mt-4 bg-gray-50 p-3 text-sm text-gray-700 border-l-2 border-blue-400">
                      <span className="font-semibold block mb-1">Relevance:</span>
                      {lab.relevance_explanation}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
