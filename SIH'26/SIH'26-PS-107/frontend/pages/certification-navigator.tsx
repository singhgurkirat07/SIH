// pages/certification-navigator.tsx
import React, { useState } from 'react';
import { Layout } from '../components/Layout';
import { EmptyState } from '../components/EmptyState';

export default function CertificationNavigator() {
  const [product, setProduct] = useState('');
  const [standardInput, setStandardInput] = useState('');
  const [hasStarted, setHasStarted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [standard, setStandard] = useState<any>(null);
  const [labCount, setLabCount] = useState(0);
  
  const generateWorkflow = async () => {
    if (!product) return;
    setIsLoading(true);
    setHasStarted(true);
    try {
      // Find standard
      const q = standardInput || product;
      const res = await fetch(`http://localhost:8000/api/explorer/standards?query=${encodeURIComponent(q)}`);
      const list = await res.json();
      if (list && list.length > 0) {
        const detRes = await fetch(`http://localhost:8000/api/explorer/standards/${list[0].id}`);
        const det = await detRes.json();
        setStandard(det);

        // Find labs
        const labRes = await fetch(`http://localhost:8000/api/labs/discovery/search`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ standard_number: det.number })
        });
        const labData = await labRes.json();
        setLabCount(labData.results?.length || 0);
      } else {
        setStandard(null);
        setLabCount(0);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <div className="p-8 max-w-4xl mx-auto h-full overflow-y-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Certification Process Navigator</h1>
        <p className="text-gray-600 mb-8 text-sm">Visualize mandatory certification workflows, required documentation, and testing dependencies based on product profiles.</p>
        
        {!hasStarted ? (
          <div className="bg-white border border-gray-300 p-6">
            <h2 className="text-lg font-semibold mb-4 border-b pb-2">Define Assessment Target</h2>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-gray-500 mb-1">Target Product</label>
                <input type="text" className="w-full p-2 border border-gray-300 text-sm" placeholder="e.g., LED Luminaires" value={product} onChange={e => setProduct(e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase text-gray-500 mb-1">Applicable Standard (Optional)</label>
                <input type="text" className="w-full p-2 border border-gray-300 text-sm" placeholder="e.g., IS 16102" value={standardInput} onChange={e => setStandardInput(e.target.value)} />
              </div>
            </div>
            <button 
              onClick={generateWorkflow}
              className="bg-blue-700 text-white px-6 py-2 text-sm font-medium hover:bg-blue-800"
            >
              Generate Technical Workflow
            </button>
          </div>
        ) : isLoading ? (
          <div className="p-10 text-center text-gray-500">Generating workflow...</div>
        ) : !standard ? (
          <div className="space-y-6">
            <EmptyState title="No Standards Found" description="Could not find a relevant standard for the provided inputs in the verified database." />
            <button onClick={() => setHasStarted(false)} className="text-blue-700 text-sm font-medium hover:underline">← Reset Assessment</button>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="bg-white border border-gray-300 p-6">
              <h2 className="text-lg font-semibold mb-4 border-b pb-2">Compliance Preparation Summary</h2>
              <div className="text-xs font-semibold text-gray-500 uppercase mb-4 px-3 py-2 bg-gray-100 inline-block border-l-4 border-amber-500">
                AI-generated informational preparation summary. Verify requirements against current official BIS publications before making compliance decisions.
              </div>
              <div className="space-y-4 text-sm">
                <div className="grid grid-cols-3 gap-4 border-b border-gray-100 pb-2">
                  <div className="font-semibold text-gray-700">Product</div>
                  <div className="col-span-2">{product}</div>
                </div>
                <div className="grid grid-cols-3 gap-4 border-b border-gray-100 pb-2">
                  <div className="font-semibold text-gray-700">Applicable Standard</div>
                  <div className="col-span-2 text-blue-700 font-medium">{standard.number}: {standard.title}</div>
                </div>
                <div className="grid grid-cols-3 gap-4 border-b border-gray-100 pb-2">
                  <div className="font-semibold text-gray-700">Certification Scheme</div>
                  <div className="col-span-2 flex items-center gap-2">
                     {standard.related_schemes && standard.related_schemes.length > 0 ? standard.related_schemes.join(', ') : 'Not specified in sources'}
                     {standard.related_schemes && standard.related_schemes.length > 0 && <span className="bg-green-100 text-green-800 text-[10px] uppercase px-1.5 py-0.5 font-bold">Verified</span>}
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4 border-b border-gray-100 pb-2">
                  <div className="font-semibold text-gray-700">Testing Required</div>
                  <div className="col-span-2">{standard.testing_information || 'Refer to standard document'}</div>
                </div>
                <div className="grid grid-cols-3 gap-4 border-b border-gray-100 pb-2">
                  <div className="font-semibold text-gray-700">Laboratories</div>
                  <div className="col-span-2 text-blue-700 font-medium cursor-pointer" onClick={() => window.location.href = '/lab-finder'}>View {labCount} Verified Labs →</div>
                </div>
              </div>
            </div>

            <div className="bg-white border border-gray-300 p-6">
              <h2 className="text-lg font-semibold mb-4 border-b pb-2">Visual Compliance Pathway</h2>
              <div className="flex items-center justify-between text-center text-sm font-medium text-gray-600 px-4 py-8">
                <div className="w-24 h-24 rounded-full border-2 border-blue-600 flex items-center justify-center bg-blue-50 text-blue-900 shadow-sm">PRODUCT</div>
                <div className="flex-1 h-0.5 bg-gray-300 relative"><div className="absolute right-0 -mt-1 w-2 h-2 border-t-2 border-r-2 border-gray-400 rotate-45"></div></div>
                <div className="w-24 h-24 rounded-full border-2 border-blue-600 flex items-center justify-center bg-blue-50 text-blue-900 shadow-sm">STANDARD</div>
                <div className="flex-1 h-0.5 bg-gray-300 relative"><div className="absolute right-0 -mt-1 w-2 h-2 border-t-2 border-r-2 border-gray-400 rotate-45"></div></div>
                <div className="w-24 h-24 rounded-full border-2 border-blue-600 flex items-center justify-center bg-blue-50 text-blue-900 shadow-sm">TESTING</div>
                <div className="flex-1 h-0.5 bg-gray-300 relative"><div className="absolute right-0 -mt-1 w-2 h-2 border-t-2 border-r-2 border-gray-400 rotate-45"></div></div>
                <div className="w-24 h-24 rounded-full border-2 border-blue-600 flex items-center justify-center bg-blue-50 text-blue-900 shadow-sm">LAB</div>
              </div>
            </div>

            <button onClick={() => setHasStarted(false)} className="text-blue-700 text-sm font-medium hover:underline">← Reset Assessment</button>
          </div>
        )}
      </div>
    </Layout>
  );
}
