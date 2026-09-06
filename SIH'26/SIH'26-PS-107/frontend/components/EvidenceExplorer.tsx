// components/EvidenceExplorer.tsx
import React, { useState } from 'react';

interface EvidenceChainItem {
  question: string;
  retrieved_source: string;
  clause_number?: string;
  answer_fragment: string;
}

interface EvidenceExplorerProps {
  answerId: number;
}

export function EvidenceExplorer({ answerId }: EvidenceExplorerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [chain, setChain] = useState<EvidenceChainItem[]>([]);

  const fetchEvidence = async () => {
    try {
      const response = await fetch(`/api/explorer/evidence/${answerId}`);
      if (response.ok) {
        const data = await response.json();
        setChain(data.chain);
        setIsOpen(true);
      }
    } catch (error) {
      console.error("Failed to fetch evidence", error);
    }
  };

  if (!isOpen) {
    return (
      <button 
        onClick={fetchEvidence}
        className="text-blue-600 hover:underline text-sm font-medium mt-2"
      >
        View evidence
      </button>
    );
  }

  return (
    <div className="mt-4 p-4 border rounded bg-gray-50 text-sm">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-bold">Evidence Chain</h3>
        <button onClick={() => setIsOpen(false)} className="text-gray-500 hover:text-black">
          Close
        </button>
      </div>
      
      {chain.map((item, idx) => (
        <div key={idx} className="mb-4 last:mb-0">
          <div className="flex items-center text-gray-500 mb-1">
            <span className="font-semibold uppercase text-xs tracking-wider">Question</span>
          </div>
          <p className="mb-2 pl-4 border-l-2 border-blue-200">{item.question}</p>
          
          <div className="flex items-center text-gray-500 mb-1">
            <span className="font-semibold uppercase text-xs tracking-wider">Retrieved Source</span>
          </div>
          <p className="mb-2 pl-4 border-l-2 border-green-200">
            {item.retrieved_source}
            {item.clause_number && <span className="ml-2 font-mono text-xs bg-gray-200 px-1 rounded">Clause {item.clause_number}</span>}
          </p>
          
          <div className="flex items-center text-gray-500 mb-1">
            <span className="font-semibold uppercase text-xs tracking-wider">Answer Fragment</span>
          </div>
          <p className="pl-4 border-l-2 border-purple-200">{item.answer_fragment}</p>
        </div>
      ))}
    </div>
  );
}
