import React, { useEffect, useState } from 'react';
import { getNMCs } from '../api';
import { ChevronDown, ChevronRight, GitMerge } from 'lucide-react';
import type { NMCCode } from '../types';

const NMCRegistryPage: React.FC = () => {
  const [nmcs, setNmcs] = useState<NMCCode[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());

  useEffect(() => {
    getNMCs()
      .then(res => setNmcs(res.data.items || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const toggleExpand = (id: number) => {
    const newExp = new Set(expanded);
    if (newExp.has(id)) newExp.delete(id);
    else newExp.add(id);
    setExpanded(newExp);
  };

  if (loading) {
    return <div className="p-12 flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-700"></div></div>;
  }

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-900 to-blue-800 rounded-xl p-8 text-white shadow-lg">
        <h1 className="text-3xl font-bold mb-2">National Material Code Registry</h1>
        <p className="text-blue-100 max-w-2xl text-sm leading-relaxed">
          The central repository of standardized materials. Each NMC acts as a single source of truth, mapping multiple disparate CPSE codes into one unified catalog for national procurement.
        </p>
      </div>

      <div className="space-y-4">
        {nmcs.map(nmc => {
          const isExp = expanded.has(nmc.id);
          return (
            <div key={nmc.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div 
                className="p-5 cursor-pointer hover:bg-gray-50 flex items-center justify-between"
                onClick={() => toggleExpand(nmc.id)}
              >
                <div className="flex items-center gap-4">
                  <div className="bg-blue-100 p-2 rounded-lg text-blue-700">
                    <GitMerge className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 font-mono tracking-tight">{nmc.nmc_code}</h3>
                    <p className="text-sm text-gray-600 mt-0.5">{nmc.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <p className="text-xs text-gray-500 font-medium">Mapped Items</p>
                    <p className="text-sm font-bold text-gray-800">{nmc.mappings?.length || 0}</p>
                  </div>
                  <div className="text-right hidden sm:block">
                    <p className="text-xs text-gray-500 font-medium">Category</p>
                    <p className="text-sm font-medium text-gray-800">{nmc.category}</p>
                  </div>
                  {isExp ? <ChevronDown className="w-5 h-5 text-gray-400" /> : <ChevronRight className="w-5 h-5 text-gray-400" />}
                </div>
              </div>

              {isExp && (
                <div className="p-8 bg-slate-50 border-t border-gray-200">
                  <div className="flex flex-col items-center justify-center">
                    
                    {/* The One Code */}
                    <div className="bg-indigo-600 text-white px-6 py-3 rounded-lg shadow-md font-mono text-lg font-bold tracking-wider relative z-10">
                      {nmc.nmc_code}
                      <div className="absolute -bottom-6 left-1/2 w-0.5 h-6 bg-indigo-300 -translate-x-1/2"></div>
                    </div>
                    
                    {/* Visual Connector horizontal bar */}
                    {(nmc.mappings && nmc.mappings.length > 0) && (
                      <div className="w-3/4 max-w-2xl h-0.5 bg-indigo-300 mt-6 relative">
                        {/* Downward stems */}
                        <div className="flex justify-between w-full absolute -top-0">
                          {nmc.mappings.map((_m, i) => (
                            <div key={i} className="w-px h-6 bg-indigo-300 relative" style={{ left: `${(i / (Math.max(1, nmc.mappings.length - 1))) * 100}%` }}></div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* The Many Codes */}
                    <div className="flex justify-between w-3/4 max-w-2xl mt-6">
                      {(nmc.mappings || []).map((mapping, _idx) => (
                        <div key={mapping.id} className="flex flex-col items-center bg-white border border-gray-200 shadow-sm rounded-lg p-3 w-32 relative group">
                          <span className="text-xs font-black text-slate-500 uppercase tracking-widest mb-2 border-b border-gray-100 pb-1 w-full text-center">
                            {mapping.cpse}
                          </span>
                          <span className="text-sm font-mono font-bold text-blue-700 text-center break-all">
                            {mapping.original_code}
                          </span>
                          
                          {/* Tooltip for hover */}
                          <div className="absolute -bottom-2 translate-y-full opacity-0 group-hover:opacity-100 transition-opacity bg-gray-800 text-white text-xs rounded py-1 px-2 pointer-events-none whitespace-nowrap z-20">
                            Status: {mapping.status}
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="mt-8 text-center text-sm font-semibold text-indigo-700 bg-indigo-50 px-4 py-2 rounded-full border border-indigo-100">
                      ONE NATION • ONE MATERIAL CODE
                    </div>
                    
                    {(!nmc.mappings || nmc.mappings.length === 0) && (
                      <div className="text-sm text-gray-500 font-sans italic mt-6">No mappings found</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
        {nmcs.length === 0 && (
          <div className="text-center p-12 bg-white rounded-xl border border-gray-200">
            <p className="text-gray-500">No National Material Codes generated yet.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default NMCRegistryPage;
