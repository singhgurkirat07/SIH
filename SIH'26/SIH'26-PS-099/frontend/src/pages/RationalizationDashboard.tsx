import React, { useState, useEffect } from 'react';
import { TrendingUp, Database, Layers, CheckCircle } from 'lucide-react';

const RationalizationDashboard: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [cpseData, setCpseData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [sumRes, oppRes, cpseRes] = await Promise.all([
        fetch('http://localhost:8000/api/rationalization/summary'),
        fetch('http://localhost:8000/api/rationalization/opportunities'),
        fetch('http://localhost:8000/api/rationalization/cpse-comparison')
      ]);
      
      if (sumRes.ok) setSummary(await sumRes.json());
      if (oppRes.ok) setOpportunities((await oppRes.json()).opportunities || []);
      if (cpseRes.ok) setCpseData((await cpseRes.json()).comparison || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !summary) {
    return <div className="text-center py-10">Loading rationalization data...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 flex items-center">
          <TrendingUp className="mr-3 text-blue-600" /> National Rationalization Dashboard
        </h1>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-gray-500">Materials Analyzed</p>
              <h3 className="text-2xl font-bold text-gray-800 mt-1">{summary.materials_analyzed}</h3>
            </div>
            <div className="p-2 bg-blue-50 rounded-lg">
              <Database className="w-5 h-5 text-blue-600" />
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Across {summary.unique_cpses} CPSEs</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-gray-500">Material Families</p>
              <h3 className="text-2xl font-bold text-gray-800 mt-1">{summary.material_families}</h3>
            </div>
            <div className="p-2 bg-indigo-50 rounded-lg">
              <Layers className="w-5 h-5 text-indigo-600" />
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Proposed NMCs: {summary.proposed_nmcs}</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-gray-500">Potential Consolidation</p>
              <h3 className="text-2xl font-bold text-gray-800 mt-1">{summary.potential_consolidation} codes</h3>
            </div>
            <div className="p-2 bg-green-50 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Current local codes: {summary.current_local_codes}</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-gray-500">Indicative Savings</p>
              <h3 className="text-2xl font-bold text-gray-800 mt-1">₹{summary.indicative_savings.toLocaleString()}</h3>
            </div>
            <div className="p-2 bg-yellow-50 rounded-lg">
              <TrendingUp className="w-5 h-5 text-yellow-600" />
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Based on historical cost</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Opportunities */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-5 border-b border-gray-200">
            <h2 className="text-lg font-bold text-gray-800">Top Rationalization Opportunities</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">CPSEs</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Local Codes</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Consolidation</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {opportunities.map((opp, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{opp.category || opp.nmc_code}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{opp.cpse_count}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{opp.local_code_count}</td>
                    <td className="px-4 py-3 text-sm text-green-600 font-medium">-{opp.potential_consolidation}</td>
                  </tr>
                ))}
                {opportunities.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-4 py-3 text-center text-sm text-gray-500">
                      No opportunities found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* CPSE Comparison */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-5 border-b border-gray-200">
            <h2 className="text-lg font-bold text-gray-800">CPSE Comparison</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">CPSE</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Materials</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Potential Duplicates</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Families</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data Completeness</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {cpseData.map((cd, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{cd.cpse}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{cd.materials}</td>
                    <td className="px-4 py-3 text-sm text-yellow-600">{cd.potential_duplicates}</td>
                    <td className="px-4 py-3 text-sm text-blue-600">{cd.families}</td>
                    <td className="px-4 py-3 text-sm">
                      <div className="flex items-center">
                        <span className="mr-2 text-gray-700">{cd.data_completeness.toFixed(0)}%</span>
                        <div className="w-16 h-2 bg-gray-200 rounded-full">
                          <div className="h-2 bg-green-500 rounded-full" style={{width: `${cd.data_completeness}%`}}></div>
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
                {cpseData.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-3 text-center text-sm text-gray-500">
                      No CPSE data found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RationalizationDashboard;
