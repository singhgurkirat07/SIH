// pages/index.tsx
import React from 'react';
import { Layout } from '../components/Layout';
import Link from 'next/link';
import { useRouter } from 'next/router';

export default function Home() {
  const router = useRouter();
  const [q, setQ] = React.useState('');

  const handleSearch = () => {
    if (q) router.push(`/find-standard?q=${encodeURIComponent(q)}`);
    else router.push(`/find-standard`);
  };

  return (
    <Layout>
      <div className="p-8 max-w-5xl mx-auto h-full overflow-y-auto">
        <header className="mb-10 pb-6 border-b border-gray-300">
          <h1 className="text-4xl font-extrabold text-gray-900 mb-2 tracking-tight">Find the right Indian Standard.</h1>
          <h2 className="text-2xl font-semibold text-gray-700 mb-6 tracking-tight">Understand what you need to comply.</h2>
          
          <div className="bg-white border border-gray-300 p-6 flex items-center shadow-sm">
            <input 
              type="text"
              placeholder="Describe your product, material, intended use or manufacturing process..."
              className="flex-1 text-base p-3 outline-none text-gray-800"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button onClick={handleSearch} className="bg-blue-700 text-white px-6 py-3 font-semibold hover:bg-blue-800 transition-colors ml-4 whitespace-nowrap">
              Find Applicable Standards
            </button>
          </div>
        </header>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          <Link href="/ask-bis" className="border border-gray-300 p-4 bg-white hover:border-blue-600 transition-colors group">
            <h3 className="font-bold text-gray-900 group-hover:text-blue-700 mb-1">ASK BIS</h3>
            <p className="text-xs text-gray-500">Query standards with citations</p>
          </Link>
          <Link href="/find-standard" className="border border-gray-300 p-4 bg-white hover:border-blue-600 transition-colors group">
            <h3 className="font-bold text-gray-900 group-hover:text-blue-700 mb-1">FIND MY STANDARD</h3>
            <p className="text-xs text-gray-500">Parametric assessment tool</p>
          </Link>
          <Link href="/certification-navigator" className="border border-gray-300 p-4 bg-white hover:border-blue-600 transition-colors group">
            <h3 className="font-bold text-gray-900 group-hover:text-blue-700 mb-1">CERTIFICATION</h3>
            <p className="text-xs text-gray-500">Process & requirements</p>
          </Link>
          <Link href="/lab-finder" className="border border-gray-300 p-4 bg-white hover:border-blue-600 transition-colors group">
            <h3 className="font-bold text-gray-900 group-hover:text-blue-700 mb-1">TESTING LABS</h3>
            <p className="text-xs text-gray-500">Find verified facilities</p>
          </Link>
        </div>

        <section className="bg-gray-50 border border-gray-300 p-8">
          <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 mb-6 text-center">How BIS Assist Works</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="w-10 h-10 rounded-full border-2 border-blue-600 text-blue-800 font-bold flex items-center justify-center mx-auto mb-3">1</div>
              <h4 className="font-bold text-gray-900 text-sm">Understand your product</h4>
            </div>
            <div>
              <div className="w-10 h-10 rounded-full border-2 border-blue-600 text-blue-800 font-bold flex items-center justify-center mx-auto mb-3">2</div>
              <h4 className="font-bold text-gray-900 text-sm">Match relevant standards</h4>
            </div>
            <div>
              <div className="w-10 h-10 rounded-full border-2 border-blue-600 text-blue-800 font-bold flex items-center justify-center mx-auto mb-3">3</div>
              <h4 className="font-bold text-gray-900 text-sm">Verify requirements</h4>
            </div>
            <div>
              <div className="w-10 h-10 rounded-full border-2 border-blue-600 text-blue-800 font-bold flex items-center justify-center mx-auto mb-3">4</div>
              <h4 className="font-bold text-gray-900 text-sm">Show supporting evidence</h4>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}
