// components/TopBar.tsx
import React from 'react';
import { FiHelpCircle, FiUser } from 'react-icons/fi';
import { useRouter } from 'next/router';

export function TopBar() {
  const { pathname } = useRouter();
  const titleMap: Record<string, string> = {
    '/': 'Home',
    '/ask-bis': 'Ask BIS',
    '/find-standard': 'Find My Standard',
    '/certification-navigator': 'Certification Navigator',
    '/standards-explorer': 'Standards Explorer',
    '/lab-finder': 'Testing Labs',
    '/hallmarking': 'Hallmarking',
    '/saved-answers': 'Saved Answers',
    '/data-sources': 'Data & Sources',
    '/settings': 'Settings',
  };
  const title = titleMap[pathname] || 'BIS Assist';

  return (
    <header className="flex items-center justify-between bg-white border-b border-gray-300 px-6 py-3">
      <h2 className="text-lg font-bold text-gray-900 tracking-tight">{title}</h2>
      <div className="flex items-center space-x-6">
        {/* Language selector */}
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold uppercase text-gray-500">Language</span>
          <select className="border border-gray-300 bg-gray-50 text-sm font-medium py-1 px-2 focus:ring-1 focus:ring-blue-600 outline-none">
            <option value="en">English (EN)</option>
            <option value="hi">हिन्दी (HI)</option>
          </select>
        </div>
        
        {/* Global Search */}
        <input
          type="text"
          placeholder="Quick reference search..."
          className="border border-gray-300 bg-gray-50 text-sm py-1.5 px-3 w-64 focus:ring-1 focus:ring-blue-600 outline-none"
        />
        
        <div className="flex items-center space-x-4 border-l border-gray-300 pl-6">
          <button className="text-gray-500 hover:text-gray-900 transition-colors">
            <FiHelpCircle size={18} />
          </button>
          <button className="flex items-center space-x-2 text-gray-500 hover:text-gray-900 transition-colors">
            <div className="bg-gray-200 rounded-full p-1">
              <FiUser size={14} className="text-gray-700" />
            </div>
            <span className="text-sm font-medium">Professional Access</span>
          </button>
        </div>
      </div>
    </header>
  );
}
