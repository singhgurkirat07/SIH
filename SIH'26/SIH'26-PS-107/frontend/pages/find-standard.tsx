// pages/find-standard.tsx
import React, { useState } from 'react';
import { Layout } from '../components/Layout';
import { EmptyState } from '../components/EmptyState';
import { useRouter } from 'next/router';

export default function FindStandard() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [conversationId] = useState(() => Math.random().toString(36).substring(7));

  React.useEffect(() => {
    if (router.query.q && typeof router.query.q === 'string' && step === 1 && !input) {
      setInput(router.query.q);
      // We don't auto handleNext to let user see it, but we could.
    }
  }, [router.query.q]);

  const handleNext = async () => {
    if (!input.trim()) return;
    setIsLoading(true);
    setStep(2);
    try {
      const res = await fetch('http://localhost:8000/api/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation_id: conversationId, message: input, language: 'en' })
      });
      const data = await res.json();
      setResult(data);
      setStep(5);
    } catch (err) {
      console.error(err);
      setStep(1);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <div className="p-8 max-w-4xl mx-auto h-full overflow-y-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Find Applicable Standard</h1>
        <p className="text-gray-600 mb-8 text-sm">Systematic evaluation of product parameters to identify mandatory and voluntary Indian Standards.</p>
        
        <div className="flex border-b border-gray-300 mb-6">
          {[1, 2, 3, 4, 5].map(num => (
            <div key={num} className={`pb-2 px-4 text-sm font-semibold uppercase ${step === num ? 'border-b-2 border-blue-700 text-blue-800' : 'text-gray-400'}`}>
              Step {num}
            </div>
          ))}
        </div>

        <div className="bg-white border border-gray-300 p-6 min-h-[300px]">
          {step === 1 && (
            <div>
              <h2 className="text-lg font-semibold mb-4">Product Classification</h2>
              <label className="block text-xs font-semibold uppercase text-gray-500 mb-1">Generic Product Description</label>
              <input 
                type="text" 
                className="w-full p-2 border border-gray-300 text-sm mb-4" 
                placeholder="Enter product type..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleNext()}
              />
              <button onClick={handleNext} className="bg-blue-700 text-white px-6 py-2 text-sm font-medium hover:bg-blue-800">
                Next Parameter →
              </button>
            </div>
          )}
          {step > 1 && step < 5 && (
            <EmptyState title="Evaluation Step" description={`Capturing parameters and analyzing compliance data...`} />
          )}
          {step === 5 && result && (
            <div>
              <h2 className="text-lg font-semibold mb-4 border-b pb-2">Decision Trace</h2>
              
              <div className="mb-6 border-l-4 border-gray-400 pl-4">
                <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">User Input</h3>
                <div className="text-sm">
                  <span className="font-semibold">Query:</span> <span>{input}</span>
                </div>
              </div>

              <div className="mb-6 border-l-4 border-blue-400 pl-4">
                <h3 className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-2">System Understanding</h3>
                <div className="grid grid-cols-2 text-sm gap-y-1">
                  <span className="font-semibold">Product:</span> <span>{result.entities.product || 'Not detected'}</span>
                  <span className="font-semibold">Material:</span> <span>{result.entities.material || 'Not detected'}</span>
                  <span className="font-semibold">Intended use:</span> <span>{result.entities.use || 'Not detected'}</span>
                  <span className="font-semibold">Capacity:</span> <span>{result.entities.capacity || 'Not detected'}</span>
                </div>
              </div>

              {result.clarification_requested ? (
                <div className="mb-6 border-l-4 border-amber-500 pl-4 bg-amber-50 p-3">
                   <h3 className="text-xs font-bold text-amber-700 uppercase tracking-wider mb-2">Clarification Needed</h3>
                   <p className="text-sm text-amber-900">{result.answer}</p>
                </div>
              ) : (
                <>
                  <div className="mb-6 border-l-4 border-green-500 pl-4 bg-green-50 p-3">
                    <h3 className="text-xs font-bold text-green-700 uppercase tracking-wider mb-2">Standard Recommendation</h3>
                    <div className="mb-2">
                      <span className="text-sm text-green-800 whitespace-pre-wrap">{result.answer}</span>
                    </div>
                  </div>

                  <div className="mb-6 border-l-4 border-amber-400 pl-4 bg-amber-50 p-3">
                    <h3 className="text-xs font-bold text-amber-700 uppercase tracking-wider mb-2">Evidence</h3>
                    {result.citations?.length > 0 ? result.citations.map((c: any, i: number) => (
                      <div key={i} className="mb-3 text-sm">
                        <div className="font-semibold">Document: <span className="font-normal">{c.document_title}</span></div>
                        <div className="italic text-gray-700 mt-1">"{c.excerpt}"</div>
                      </div>
                    )) : (
                      <div className="text-sm text-amber-900">Not verified in available sources.</div>
                    )}
                  </div>
                </>
              )}

              <div className="border-t border-gray-200 pt-4 mt-6">
                <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Next Compliance Step</h3>
                <div className="flex gap-4">
                  <button onClick={() => window.location.href = '/certification-navigator'} className="bg-blue-700 text-white px-4 py-2 text-sm font-medium hover:bg-blue-800 transition-colors">
                    Testing / certification information →
                  </button>
                  <button onClick={() => setStep(1)} className="bg-white border border-gray-300 text-gray-700 px-4 py-2 text-sm font-medium hover:bg-gray-50 transition-colors">
                    Start Over
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
