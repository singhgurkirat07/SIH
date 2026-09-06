import React, { useEffect, useState } from 'react';
import { getMatches, approveMatch, rejectMatch } from '../api';
import { CheckCircle2, XCircle, AlertTriangle, AlertCircle, Edit, RefreshCw } from 'lucide-react';
import type { MatchResult, Explanation } from '../types';

const ReviewQueuePage: React.FC = () => {
  const [matches, setMatches] = useState<MatchResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [actioningId, setActioningId] = useState<number | null>(null);

  useEffect(() => {
    fetchQueue();
  }, []);

  const fetchQueue = async () => {
    try {
      const res = await getMatches({ status: 'pending' });
      setMatches(res.data.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: number) => {
    setActioningId(id);
    try {
      await approveMatch(id);
      setMatches(matches.filter(m => m.id !== id));
    } catch (err) {
      console.error(err);
    } finally {
      setActioningId(null);
    }
  };

  const handleReject = async (id: number) => {
    setActioningId(id);
    try {
      await rejectMatch(id);
      setMatches(matches.filter(m => m.id !== id));
    } catch (err) {
      console.error(err);
    } finally {
      setActioningId(null);
    }
  };

  const parseExplanation = (expStr: string | null): Explanation | null => {
    if (!expStr) return null;
    try {
      return JSON.parse(expStr);
    } catch {
      return null;
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.9) return 'bg-green-500';
    if (score >= 0.75) return 'bg-amber-500';
    return 'bg-red-500';
  };

  if (loading) {
    return <div className="p-12 flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-700"></div></div>;
  }

  const highConfidence = matches.filter(m => m.confidence_score >= 0.9).length;
  const medConfidence = matches.filter(m => m.confidence_score >= 0.75 && m.confidence_score < 0.9).length;
  const lowConfidence = matches.filter(m => m.confidence_score < 0.75).length;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Human Review Queue</h1>
          <p className="text-sm text-gray-500 mt-1">Review and approve AI-recommended material matches</p>
        </div>
      </div>

      <div className="flex bg-white rounded-lg shadow-sm border border-gray-200 p-4 gap-6">
        <div className="flex-1 border-r border-gray-200 last:border-0 pr-6 last:pr-0">
          <p className="text-sm text-gray-500 font-medium mb-1">Total Pending</p>
          <p className="text-2xl font-bold text-gray-900">{matches.length}</p>
        </div>
        <div className="flex-1 border-r border-gray-200 last:border-0 pr-6 last:pr-0">
          <p className="text-sm text-gray-500 font-medium mb-1">High Confidence</p>
          <p className="text-2xl font-bold text-green-600">{highConfidence}</p>
        </div>
        <div className="flex-1 border-r border-gray-200 last:border-0 pr-6 last:pr-0">
          <p className="text-sm text-gray-500 font-medium mb-1">Medium Confidence</p>
          <p className="text-2xl font-bold text-amber-600">{medConfidence}</p>
        </div>
        <div className="flex-1">
          <p className="text-sm text-gray-500 font-medium mb-1">Low Confidence</p>
          <p className="text-2xl font-bold text-red-600">{lowConfidence}</p>
        </div>
      </div>

        <div className="space-y-8">
          {matches.map(match => {
            const exp = parseExplanation(match.explanation);
            const isActioning = actioningId === match.id;
            
            return (
              <div key={match.id} className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
                {/* Header: Confidence & Recommendation */}
                <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white flex justify-between items-center">
                  <div className="flex items-center gap-4">
                    <span className={`px-3 py-1.5 rounded-md text-sm font-bold uppercase tracking-wider ${
                      match.match_type === 'IDENTICAL' ? 'bg-green-100 text-green-800 border border-green-200' :
                      match.match_type === 'DIFFERENT' ? 'bg-red-100 text-red-800 border border-red-200' :
                      match.match_type === 'INSUFFICIENT_INFO' ? 'bg-gray-100 text-gray-800 border border-gray-200' :
                      'bg-blue-100 text-blue-800 border border-blue-200'
                    }`}>
                      {match.match_type.replace('_', ' ')}
                    </span>
                    <div className="flex items-center gap-2 border-l border-gray-300 pl-4">
                      <span className="text-sm font-medium text-gray-600">AI Confidence:</span>
                      <div className="w-32 bg-gray-200 rounded-full h-2.5 overflow-hidden">
                        <div 
                          className={`h-full ${getConfidenceColor(match.confidence_score)}`} 
                          style={{ width: `${Math.max(0, Math.min(100, match.confidence_score))}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-bold text-gray-800">{match.confidence_score.toFixed(1)}%</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-500 font-medium">Recommended NMC:</span>
                    <span className="font-mono text-lg font-bold text-indigo-700 bg-indigo-50 px-3 py-1 rounded border border-indigo-100">
                      {match.common_national_code || 'MANUAL-REVIEW'}
                    </span>
                  </div>
                </div>

                {/* Core Comparison Matrix */}
                <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-gray-200 bg-white">
                  
                  {/* Material A */}
                  <div className="p-6 space-y-4 relative">
                    <div className="absolute top-6 right-6 px-2 py-0.5 rounded text-xs font-bold bg-gray-100 text-gray-600 border border-gray-300">
                      {match.material_a.cpse}
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Source Material A</h4>
                      <div className="font-mono text-sm text-blue-600 font-medium mb-3">{match.material_a.material_code}</div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded border border-gray-200">
                      <h5 className="text-xs font-semibold text-gray-500 uppercase mb-1">Original Description</h5>
                      <p className="text-sm font-medium text-gray-900">{match.material_a.description}</p>
                    </div>
                    {match.material_a.normalized_description && (
                      <div className="bg-blue-50/50 p-3 rounded border border-blue-100">
                        <h5 className="text-xs font-semibold text-blue-600 uppercase mb-1">Normalized Attributes</h5>
                        <p className="text-sm text-blue-900">{match.material_a.normalized_description}</p>
                      </div>
                    )}
                  </div>

                  {/* Material B */}
                  <div className="p-6 space-y-4 relative">
                    <div className="absolute top-6 right-6 px-2 py-0.5 rounded text-xs font-bold bg-gray-100 text-gray-600 border border-gray-300">
                      {match.material_b.cpse}
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Source Material B</h4>
                      <div className="font-mono text-sm text-blue-600 font-medium mb-3">{match.material_b.material_code}</div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded border border-gray-200">
                      <h5 className="text-xs font-semibold text-gray-500 uppercase mb-1">Original Description</h5>
                      <p className="text-sm font-medium text-gray-900">{match.material_b.description}</p>
                    </div>
                    {match.material_b.normalized_description && (
                      <div className="bg-blue-50/50 p-3 rounded border border-blue-100">
                        <h5 className="text-xs font-semibold text-blue-600 uppercase mb-1">Normalized Attributes</h5>
                        <p className="text-sm text-blue-900">{match.material_b.normalized_description}</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Similarity Metrics breakdown */}
                <div className="px-6 py-4 bg-white border-t border-gray-200">
                  <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Similarity Components</h4>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    <div>
                      <div className="flex justify-between text-xs mb-1"><span className="text-gray-600">Semantic</span><span className="font-medium">{(match.semantic_similarity * 100).toFixed(0)}%</span></div>
                      <div className="w-full bg-gray-100 rounded h-1.5"><div className="bg-indigo-500 h-1.5 rounded" style={{width: `${match.semantic_similarity * 100}%`}}></div></div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1"><span className="text-gray-600">Attribute</span><span className="font-medium">{(match.attribute_similarity * 100).toFixed(0)}%</span></div>
                      <div className="w-full bg-gray-100 rounded h-1.5"><div className="bg-blue-500 h-1.5 rounded" style={{width: `${match.attribute_similarity * 100}%`}}></div></div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1"><span className="text-gray-600">Technical</span><span className="font-medium">{(match.technical_similarity * 100).toFixed(0)}%</span></div>
                      <div className="w-full bg-gray-100 rounded h-1.5"><div className="bg-teal-500 h-1.5 rounded" style={{width: `${match.technical_similarity * 100}%`}}></div></div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1"><span className="text-gray-600">Text</span><span className="font-medium">{(match.text_similarity * 100).toFixed(0)}%</span></div>
                      <div className="w-full bg-gray-100 rounded h-1.5"><div className="bg-amber-500 h-1.5 rounded" style={{width: `${match.text_similarity * 100}%`}}></div></div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1"><span className="text-gray-600">Category</span><span className="font-medium">{(match.category_similarity * 100).toFixed(0)}%</span></div>
                      <div className="w-full bg-gray-100 rounded h-1.5"><div className="bg-purple-500 h-1.5 rounded" style={{width: `${match.category_similarity * 100}%`}}></div></div>
                    </div>
                  </div>
                </div>

                {/* AI Reasoning Section */}
                {exp && (
                  <div className="p-6 bg-slate-50 border-t border-gray-200">
                    <h4 className="text-sm font-bold text-slate-800 mb-4 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-2 text-slate-500" />
                      AI Decision Logic
                    </h4>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-5">
                      <div>
                        <h5 className="text-xs font-bold text-emerald-700 uppercase tracking-wider mb-3 flex items-center border-b border-emerald-200 pb-2">
                          <CheckCircle2 className="w-4 h-4 mr-1.5" /> Matching Attributes
                        </h5>
                        {exp.reasons.length > 0 ? (
                          <ul className="space-y-2.5">
                            {exp.reasons.map((r, i) => (
                              <li key={i} className="text-sm text-slate-700 flex items-start bg-emerald-50/50 p-2 rounded">
                                <span className="text-emerald-500 mr-2 mt-0.5">•</span>
                                {r.detail}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-sm text-slate-500 italic">No significant matching attributes found.</p>
                        )}
                      </div>
                      
                      <div>
                        <h5 className="text-xs font-bold text-rose-700 uppercase tracking-wider mb-3 flex items-center border-b border-rose-200 pb-2">
                          <AlertTriangle className="w-4 h-4 mr-1.5" /> Key Differences & Missing Info
                        </h5>
                        {exp.differences.length > 0 ? (
                          <ul className="space-y-2.5">
                            {exp.differences.map((d, i) => (
                              <li key={i} className="text-sm text-slate-700 flex items-start bg-rose-50/50 p-2 rounded">
                                <span className="text-rose-500 mr-2 mt-0.5">•</span>
                                {d.detail}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-sm text-slate-500 italic">No significant differences detected.</p>
                        )}
                      </div>
                    </div>
                    
                    <div className="bg-white p-4 border border-slate-200 rounded-lg shadow-sm">
                      <h5 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">System Summary</h5>
                      <p className="text-sm text-slate-800 font-medium leading-relaxed">
                        {exp.summary}
                      </p>
                      <p className="text-sm text-indigo-700 font-semibold mt-2">
                        {exp.recommendation}
                      </p>
                    </div>

                    {exp.why_not_merge && (
                      <div className="bg-red-50 p-4 border border-red-200 rounded-lg shadow-sm mt-4">
                        <h5 className="text-xs font-bold text-red-600 uppercase tracking-wider mb-2 flex items-center">
                          <XCircle className="w-4 h-4 mr-1" /> WHY NOT MERGE?
                        </h5>
                        
                        <div className="space-y-3">
                          {exp.why_not_merge.matching_attributes?.length > 0 && (
                            <div>
                              <p className="text-sm font-medium text-gray-700">Matching Attributes:</p>
                              <ul className="list-disc pl-5 text-sm text-gray-600">
                                {exp.why_not_merge.matching_attributes.map((a: any, i: number) => (
                                  <li key={i}>{a.name} ({a.value})</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {exp.why_not_merge.conflicting_attributes?.length > 0 && (
                            <div>
                              <p className="text-sm font-medium text-gray-700">Conflicting Attributes:</p>
                              <ul className="list-disc pl-5 text-sm text-red-700">
                                {exp.why_not_merge.conflicting_attributes.map((a: any, i: number) => (
                                  <li key={i}>
                                    <span className="font-semibold">{a.name} differs:</span> {a.value_a} vs {a.value_b}
                                    {a.severity === 'CRITICAL' && <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-200 text-red-800 uppercase">Critical Conflict</span>}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {exp.why_not_merge.missing_attributes?.length > 0 && (
                            <div>
                              <p className="text-sm font-medium text-gray-700">Missing Information:</p>
                              <ul className="list-disc pl-5 text-sm text-gray-600">
                                {exp.why_not_merge.missing_attributes.map((a: any, i: number) => (
                                  <li key={i}>{a.name} is missing in one material</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          <div className="pt-2 border-t border-red-200 mt-3">
                            <p className="text-sm mt-2"><span className="font-bold text-gray-800">Decision:</span> <span className="font-mono text-red-700 font-bold">{exp.why_not_merge.decision}</span></p>
                            <p className="text-sm"><span className="font-bold text-gray-800">Reason:</span> {exp.why_not_merge.reason}</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Actions */}
                <div className="px-6 py-4 bg-gray-100 border-t border-gray-200 flex justify-between items-center">
                  <div className="flex gap-3">
                    <button className="flex items-center px-3 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 shadow-sm transition-colors">
                      <Edit className="w-4 h-4 mr-2" />
                      Modify NMC
                    </button>
                    <button className="flex items-center px-3 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 shadow-sm transition-colors">
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Re-evaluate
                    </button>
                  </div>
                  <div className="flex gap-3">
                    <button 
                      onClick={() => handleReject(match.id)}
                      disabled={isActioning}
                      className="flex items-center px-5 py-2.5 text-sm font-bold text-rose-700 bg-white border border-rose-300 rounded-lg hover:bg-rose-50 disabled:opacity-50 shadow-sm transition-colors"
                    >
                      <XCircle className="w-4 h-4 mr-2" />
                      Reject Match
                    </button>
                    <button 
                      onClick={() => handleApprove(match.id)}
                      disabled={isActioning}
                      className="flex items-center px-5 py-2.5 text-sm font-bold text-white bg-emerald-600 border border-emerald-600 rounded-lg hover:bg-emerald-700 disabled:opacity-50 shadow-sm transition-colors"
                    >
                      <CheckCircle2 className="w-4 h-4 mr-2" />
                      Approve & Map to NMC
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
    </div>
  );
};

export default ReviewQueuePage;
