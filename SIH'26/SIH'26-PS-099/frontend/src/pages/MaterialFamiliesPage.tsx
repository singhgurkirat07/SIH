import React, { useState, useEffect } from 'react';
import { Layers } from 'lucide-react';

const MaterialFamiliesPage: React.FC = () => {
  const [families, setFamilies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFamily, setSelectedFamily] = useState<any | null>(null);

  useEffect(() => {
    fetchFamilies();
  }, []);

  const fetchFamilies = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:8000/api/material-families');
      if (res.ok) {
        const data = await res.json();
        setFamilies(data.families || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 flex items-center">
          <Layers className="mr-3 text-blue-600" /> Material Families
        </h1>
      </div>

      {loading ? (
        <div className="text-center py-10">Loading material families...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Family ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Canonical Material</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CPSEs</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Local Codes</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">NMC</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {families.map((fam) => (
                    <tr 
                      key={fam.id} 
                      className={`hover:bg-blue-50 cursor-pointer ${selectedFamily?.id === fam.id ? 'bg-blue-50' : ''}`}
                      onClick={() => setSelectedFamily(fam)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">FAM-{fam.id}</td>
                      <td className="px-6 py-4 text-sm text-gray-900 truncate max-w-xs" title={fam.canonical_description}>
                        {fam.canonical_description}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{fam.cpse_count}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{fam.local_code_count}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{fam.nmc_code}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          {fam.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {families.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-4 text-center text-sm text-gray-500">
                        No material families found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="lg:col-span-1">
            {selectedFamily ? (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sticky top-6">
                <h2 className="text-lg font-bold text-gray-800 mb-4 border-b pb-2">National Material Family</h2>
                
                <div className="space-y-4">
                  <div>
                    <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Canonical Description</span>
                    <p className="mt-1 text-sm font-medium text-gray-900">{selectedFamily.canonical_description}</p>
                  </div>
                  
                  <div>
                    <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Proposed NMC</span>
                    <p className="mt-1 text-sm text-blue-600 font-mono font-bold bg-blue-50 py-1 px-2 rounded inline-block">{selectedFamily.nmc_code}</p>
                  </div>

                  <div>
                    <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Common Attributes</span>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {Object.entries(selectedFamily.common_attributes).map(([k, v]) => (
                        <span key={k} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          <span className="mr-1 text-gray-500">{k}:</span> {String(v)}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="border-t pt-4">
                    <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold block mb-2">CPSE Coverage</span>
                    <div className="flex flex-wrap gap-2">
                      {selectedFamily.cpses.map((c: string) => (
                         <span key={c} className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100">
                           {c}
                         </span>
                      ))}
                    </div>
                  </div>

                  <div className="border-t pt-4">
                    <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold block mb-2">Local Codes</span>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {selectedFamily.member_materials.map((m: any) => (
                        <div key={m.id} className="text-sm bg-gray-50 p-2 rounded flex justify-between items-center">
                          <span className="font-mono text-gray-600">{m.cpse} / {m.material_code}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="border-t pt-4">
                    <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold block mb-2">Evidence</span>
                    <p className="text-sm text-gray-600">
                      Grouped based on approved strong equivalent matches between member materials.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-gray-50 rounded-xl border border-gray-200 p-10 text-center text-gray-500 flex flex-col items-center justify-center h-full">
                <Layers className="w-12 h-12 text-gray-300 mb-3" />
                <p>Select a material family from the table to view details.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MaterialFamiliesPage;
