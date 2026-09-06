// components/EvidenceRail.tsx
import React from 'react';

interface Citation {
  id: number;
  standard: string;
  clause: string;
  page?: string;
  text: string;
  confidence: string; // 'Supported by source' | 'Multiple relevant sources found' | 'Potential match, verify before compliance decision'
}

export function EvidenceRail({ citation }: { citation: Citation }) {
  const isHighConfidence = citation.confidence === 'Supported by source';
  const isMedium = citation.confidence === 'Multiple relevant sources found';
  
  return (
    <div className="border border-gray-200 text-sm">
      <div className={`px-3 py-2 border-b flex items-center justify-between ${isHighConfidence ? 'bg-blue-50 border-blue-200 text-blue-900' : isMedium ? 'bg-amber-50 border-amber-200 text-amber-900' : 'bg-gray-100 border-gray-300 text-gray-800'}`}>
        <span className="font-semibold text-xs uppercase tracking-wide">{citation.confidence}</span>
      </div>
      
      <div className="p-3 bg-white">
        <div className="mb-3">
          <div className="text-xs text-gray-500 uppercase tracking-wide font-semibold mb-1">Source Document</div>
          <div className="font-medium text-gray-900">{citation.standard}</div>
          <div className="text-gray-600 text-xs mt-0.5">
            Clause {citation.clause} {citation.page && `| Page ${citation.page}`}
          </div>
        </div>
        
        <div>
          <div className="text-xs text-gray-500 uppercase tracking-wide font-semibold mb-1">Verified Excerpt</div>
          <div className="p-2 bg-gray-50 border-l-2 border-gray-400 font-serif text-gray-800 leading-relaxed italic">
            "{citation.text}"
          </div>
        </div>
        
        <div className="mt-4 pt-3 border-t border-gray-100">
          <a href="#" className="text-blue-700 hover:underline font-medium text-xs flex items-center">
            Open Original Source ↗
          </a>
        </div>
      </div>
    </div>
  );
}
