import React, { useEffect, useState } from 'react';
import { 
  Database, 
  Copy, 
  GitMerge, 
  CheckCircle, 
  Clock, 
  Upload,
  Play,
  AlertCircle,
  TrendingUp
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { getDashboard, seedDatabase, runGoldenTest, getGoldenTestResults } from '../api';
import type { DashboardData, GoldenTestMetrics } from '../types';

const COLORS = ['#1e40af', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#64748b'];

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [goldenMetrics, setGoldenMetrics] = useState<GoldenTestMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const res = await getDashboard();
      setData(res.data);
      
      const metricsRes = await getGoldenTestResults();
      if (metricsRes.data && metricsRes.data.total_pairs > 0) {
        setGoldenMetrics(metricsRes.data);
      }
    } catch (err) {
      console.error("Failed to load dashboard data", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSeed = async () => {
    setSeeding(true);
    try {
      await seedDatabase();
      await fetchDashboard();
    } catch (err) {
      console.error(err);
    } finally {
      setSeeding(false);
    }
  };

  const handleRunTest = async () => {
    try {
      const res = await runGoldenTest();
      setGoldenMetrics(res.data);
    } catch (err) {
      console.error(err);
    }
  };


  if (loading) {
    return <div className="p-8 flex justify-center items-center h-full"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-700"></div></div>;
  }

  if (!data || data.total_materials === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[70vh] bg-white rounded-lg border border-gray-200 p-8 text-center shadow-sm">
        <Database className="w-16 h-16 text-blue-300 mb-4" />
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Welcome to NUMM Platform</h2>
        <p className="text-gray-500 mb-8 max-w-md">No materials data found in the system. Start by uploading a CSV file or seed the database with synthetic demo data for SIH 2026.</p>
        <div className="flex gap-4">
          <button 
            onClick={handleSeed} 
            disabled={seeding}
            className="flex items-center px-6 py-2.5 bg-blue-700 text-white font-medium rounded-lg hover:bg-blue-800 transition-colors disabled:opacity-50"
          >
            {seeding ? 'Seeding...' : 'Seed Demo Data'}
          </button>
          <button className="flex items-center px-6 py-2.5 bg-white border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors">
            <Upload className="w-4 h-4 mr-2" />
            Upload Materials
          </button>
        </div>
      </div>
    );
  }

  const matchTypeData = Object.entries(data.match_type_distribution || {}).map(([name, value]) => ({ name, value }));
  const cpseData = Object.entries(data.cpse_counts || {}).map(([name, value]) => ({ name, value }));
  const categoryData = Object.entries(data.category_counts || {}).map(([name, value]) => ({ name, value })).sort((a,b)=>b.value-a.value).slice(0, 5);
  const confidenceData = [
    { name: 'High (≥90)', value: data.confidence_distribution['high'] || data.confidence_distribution['High'] || 0 },
    { name: 'Medium (75-89)', value: data.confidence_distribution['medium'] || data.confidence_distribution['Medium'] || 0 },
    { name: 'Low (<75)', value: data.confidence_distribution['low'] || data.confidence_distribution['Low'] || 0 }
  ];

  return (
    <div className="space-y-6 relative">
      {/* Synthetic Data Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white px-4 py-3 rounded-lg shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-blue-200" />
          <div>
            <p className="text-sm font-bold tracking-wide">LIVE DEMONSTRATION MODE</p>
            <p className="text-xs text-blue-100">Displaying system analytics based on synthetic CPSE dataset for SIH 2026 Evaluation. Financial metrics are indicative.</p>
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Unified Analytics Dashboard</h1>
        <p className="text-sm text-gray-500 font-medium">Data Sync: Real-time</p>
      </div>

      {/* Primary KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-blue-50 rounded-xl p-5 border border-blue-100 flex flex-col justify-between shadow-sm">
          <div className="flex justify-between items-start mb-2">
            <span className="text-sm font-bold text-blue-900 uppercase tracking-wider">Materials Processed</span>
            <Database className="w-5 h-5 text-blue-500" />
          </div>
          <span className="text-3xl font-black text-blue-900">{data.total_materials.toLocaleString()}</span>
        </div>
        
        <div className="bg-amber-50 rounded-xl p-5 border border-amber-100 flex flex-col justify-between shadow-sm">
          <div className="flex justify-between items-start mb-2">
            <span className="text-sm font-bold text-amber-900 uppercase tracking-wider">Duplicates Detected</span>
            <Copy className="w-5 h-5 text-amber-500" />
          </div>
          <span className="text-3xl font-black text-amber-900">{data.duplicates_detected.toLocaleString()}</span>
        </div>

        <div className="bg-purple-50 rounded-xl p-5 border border-purple-100 flex flex-col justify-between shadow-sm">
          <div className="flex justify-between items-start mb-2">
            <span className="text-sm font-bold text-purple-900 uppercase tracking-wider">Equivalences Found</span>
            <GitMerge className="w-5 h-5 text-purple-500" />
          </div>
          <span className="text-3xl font-black text-purple-900">{data.potential_equivalences.toLocaleString()}</span>
        </div>

        <div className="bg-emerald-50 rounded-xl p-5 border border-emerald-100 flex flex-col justify-between shadow-sm relative overflow-hidden">
          <div className="absolute -right-4 -bottom-4 opacity-10">
            <TrendingUp className="w-24 h-24 text-emerald-900" />
          </div>
          <div className="flex justify-between items-start mb-2">
            <span className="text-sm font-bold text-emerald-900 uppercase tracking-wider">Indicative Savings</span>
            <TrendingUp className="w-5 h-5 text-emerald-500" />
          </div>
          <span className="text-3xl font-black text-emerald-900 relative z-10">₹{(data.estimated_savings / 100000).toFixed(1)}L</span>
        </div>
      </div>

      {/* Secondary KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-200 flex items-center justify-between shadow-sm">
          <div>
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1">Pending Reviews</span>
            <span className="text-xl font-bold text-gray-900">{data.pending_reviews.toLocaleString()}</span>
          </div>
          <div className="bg-orange-100 p-3 rounded-lg"><Clock className="w-5 h-5 text-orange-600" /></div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-200 flex items-center justify-between shadow-sm">
          <div>
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1">Approved Mappings</span>
            <span className="text-xl font-bold text-gray-900">{data.approved_matches?.toLocaleString() || 0}</span>
          </div>
          <div className="bg-green-100 p-3 rounded-lg"><CheckCircle className="w-5 h-5 text-green-600" /></div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-200 flex items-center justify-between shadow-sm">
          <div>
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1">NMCs Generated</span>
            <span className="text-xl font-bold text-indigo-900">{data.total_nmc_generated?.toLocaleString() || 0}</span>
          </div>
          <div className="bg-indigo-100 p-3 rounded-lg"><CheckCircle className="w-5 h-5 text-indigo-600" /></div>
        </div>
      </div>
      {/* Main Content Sections */}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Match Type Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={matchTypeData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {matchTypeData.map((_entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">CPSE-wise Material Count</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={cpseData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" axisLine={false} tickLine={false} />
                <YAxis axisLine={false} tickLine={false} />
                <Tooltip cursor={{fill: '#f3f4f6'}} />
                <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Confidence Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={confidenceData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" axisLine={false} tickLine={false} />
                <YAxis axisLine={false} tickLine={false} />
                <Tooltip cursor={{fill: '#f3f4f6'}} />
                <Bar dataKey="value" fill="#10b981" radius={[4, 4, 0, 0]}>
                  {confidenceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.name === 'High' ? '#10b981' : entry.name === 'Medium' ? '#f59e0b' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Top Categories</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData} layout="vertical" margin={{ left: 40 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" axisLine={false} tickLine={false} />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} width={100} />
                <Tooltip cursor={{fill: '#f3f4f6'}} />
                <Bar dataKey="value" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800">Recent Activity</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-100">
                {(data.recent_activity || []).map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-5 py-3 text-sm text-gray-500 whitespace-nowrap">{new Date(log.timestamp).toLocaleString()}</td>
                    <td className="px-5 py-3 text-sm text-gray-900">{log.user}</td>
                    <td className="px-5 py-3 text-sm text-gray-700">{log.action} <span className="text-gray-400 text-xs ml-1">{log.details}</span></td>
                  </tr>
                ))}
                {(!data.recent_activity || data.recent_activity.length === 0) && (
                  <tr>
                    <td colSpan={3} className="px-5 py-8 text-center text-sm text-gray-500">No recent activity</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Model Evaluation</h3>
            <button onClick={handleRunTest} className="text-blue-600 hover:bg-blue-50 p-1.5 rounded-md transition-colors">
              <Play className="w-4 h-4" />
            </button>
          </div>
          <p className="text-sm text-gray-500 mb-6">Run Golden Dataset evaluation to measure current model accuracy.</p>
          
          {goldenMetrics ? (
            <div className="space-y-4">
              <div className="flex justify-between text-sm text-gray-500 mb-2">
                <span>Test samples: <strong className="text-gray-700">{goldenMetrics.total_pairs}</strong></span>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">Accuracy</span>
                  <span className="text-sm font-bold text-indigo-700">{(goldenMetrics.accuracy * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${goldenMetrics.accuracy * 100}%` }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">F1 Score</span>
                  <span className="text-sm font-bold text-blue-700">{(goldenMetrics.f1 * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${goldenMetrics.f1 * 100}%` }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">Precision</span>
                  <span className="text-sm font-bold text-emerald-600">{(goldenMetrics.precision * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${goldenMetrics.precision * 100}%` }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">Recall</span>
                  <span className="text-sm font-bold text-amber-600">{(goldenMetrics.recall * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-amber-500 h-2 rounded-full" style={{ width: `${goldenMetrics.recall * 100}%` }}></div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-6 border-2 border-dashed border-gray-200 rounded-lg">
              <span className="text-sm text-gray-500">Metrics not available. Run test to view.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
