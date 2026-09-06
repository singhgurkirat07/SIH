import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getRerankerStatus, getSavingsTrend } from '../api';
import type { RerankerStatus } from '../types';

const AnalyticsPage: React.FC = () => {
  const [rerankerStatus, setRerankerStatus] = useState<RerankerStatus | null>(null);
  const [savingsTrend, setSavingsTrend] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [rerankerRes, savingsRes] = await Promise.all([
          getRerankerStatus(),
          getSavingsTrend()
        ]);
        setRerankerStatus(rerankerRes.data);
        setSavingsTrend(savingsRes.data);
      } catch (err) {
        setError('Failed to load analytics data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="p-12 flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-700"></div></div>;
  }

  if (error) {
    return <div className="p-12 text-center text-red-600 font-medium">{error}</div>;
  }

  const feedbackCount = rerankerStatus?.feedback_count || 0;
  const minRequired = rerankerStatus?.min_required || 50;
  const progressPercent = Math.min(100, Math.max(0, (feedbackCount / minRequired) * 100));
  const isRetrainingAvailable = feedbackCount >= minRequired;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Analytics & Reporting</h1>
        <p className="text-sm text-gray-500 mt-1">System performance and data insights</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Indicative Savings Over Time</h3>
          <div className="h-64">
            {savingsTrend.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={savingsTrend}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} />
                  <YAxis axisLine={false} tickLine={false} />
                  <Tooltip cursor={{fill: '#f3f4f6'}} />
                  <Bar dataKey="value" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex flex-col justify-center items-center text-gray-400">
                <span className="text-sm">Insufficient historical data for meaningful time series.</span>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-center items-center text-center">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Model Retraining</h3>
          <p className="text-gray-500 text-sm mb-6 max-w-sm">
            The active learning module requires at least {minRequired} human feedbacks to initiate a fine-tuning cycle.
          </p>
          
          <div className="w-full max-w-xs mb-2">
            <div className="flex justify-between text-sm mb-1">
              <span className="font-medium text-gray-700">Feedback Collected</span>
              <span className="font-bold text-blue-600">{feedbackCount} / {minRequired}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${progressPercent}%` }}></div>
            </div>
          </div>
          
          <button 
            disabled={!isRetrainingAvailable} 
            className={`mt-4 px-4 py-2 font-medium rounded-lg border transition-colors ${
              isRetrainingAvailable 
                ? 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700' 
                : 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
            }`}
          >
            {isRetrainingAvailable ? 'Train Reranker' : 'Insufficient feedback for retraining'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
