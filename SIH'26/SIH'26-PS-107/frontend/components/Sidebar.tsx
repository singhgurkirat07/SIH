// components/Sidebar.tsx
import Link from 'next/link';
import { useRouter } from 'next/router';
import { FiHome, FiMessageSquare, FiSearch, FiFolder, FiList, FiTool, FiAward, FiBookmark, FiSettings, FiInfo } from 'react-icons/fi';

const navItems = [
  { href: '/', label: 'Home', icon: <FiHome /> },
  { href: '/ask-bis', label: 'Ask BIS', icon: <FiMessageSquare /> },
  { href: '/find-standard', label: 'Find My Standard', icon: <FiSearch /> },
  { href: '/certification-navigator', label: 'Certification Navigator', icon: <FiFolder /> },
  { href: '/standards-explorer', label: 'Standards Explorer', icon: <FiList /> },
  { href: '/lab-finder', label: 'Testing Labs', icon: <FiTool /> },
];

const bottomItems: any[] = [
];

export function Sidebar() {
  const { pathname } = useRouter();
  
  const renderItem = (item: typeof navItems[0]) => {
    const isActive = pathname === item.href;
    return (
      <Link key={item.href} href={item.href} legacyBehavior>
        <a className={`flex items-center space-x-3 px-3 py-2 text-sm transition-colors ${isActive ? 'bg-blue-50 border-l-4 border-blue-700 text-blue-900 font-semibold' : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900 border-l-4 border-transparent'}`}>
          <span className="text-lg opacity-75">{item.icon}</span>
          <span>{item.label}</span>
        </a>
      </Link>
    );
  };

  return (
    <nav className="w-64 bg-gray-50 border-r border-gray-300 flex flex-col h-screen overflow-y-auto shrink-0">
      <div className="p-5 border-b border-gray-300 bg-white">
        <h1 className="text-xl font-extrabold text-gray-900 tracking-tight">BIS ASSIST</h1>
        <p className="text-xs text-gray-500 font-medium mt-1 uppercase tracking-wider">Indian Standards & Services</p>
      </div>
      
      <div className="flex-1 py-4 space-y-1">
        {navItems.map(renderItem)}
      </div>
      
      <div className="py-4 border-t border-gray-300 space-y-1 bg-white">
        {bottomItems.map(renderItem)}
      </div>
    </nav>
  );
}
