import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Database, 
  GitCompare, 
  ClipboardCheck, 
  BookOpen, 
  BarChart3, 
  History, 
  Code,
  Search,
  Menu
} from 'lucide-react';

const Layout: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'National Rationalization', path: '/rationalization', icon: BarChart3 },
    { name: 'Material Families', path: '/material-families', icon: Database },
    { name: 'Materials', path: '/materials', icon: Database },
    { name: 'Matching', path: '/matching', icon: GitCompare },
    { name: 'Review Queue', path: '/review', icon: ClipboardCheck, badge: '5' },
    { name: 'NMC Registry', path: '/nmc', icon: BookOpen },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Audit Trail', path: '/audit', icon: History },
    { name: 'API / Integration', path: '/api-docs', icon: Code },
  ];

  return (
    <div className="flex h-screen bg-gray-50 font-sans">
      {/* Mobile sidebar backdrop */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 z-20 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        ></div>
      )}

      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-30 w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 lg:translate-x-0 lg:static lg:inset-auto ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center justify-center h-16 border-b border-gray-200 px-4 bg-blue-900 text-white">
          <div className="flex flex-col items-center">
            <h1 className="text-sm font-bold text-center leading-tight">National Unified Material Master</h1>
            <span className="text-[10px] text-blue-200 font-medium tracking-wide uppercase mt-0.5">One Nation • One Material Code</span>
          </div>
        </div>
        
        <nav className="p-4 space-y-1 overflow-y-auto h-[calc(100vh-4rem)]">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`
              }
              onClick={() => setIsMobileMenuOpen(false)}
            >
              <item.icon className="w-5 h-5 mr-3 flex-shrink-0" />
              <span className="flex-1">{item.name}</span>
              {item.badge && (
                <span className="bg-red-100 text-red-600 py-0.5 px-2 rounded-full text-xs font-bold">
                  {item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 lg:px-8 z-10 shadow-sm">
          <div className="flex items-center">
            <button
              onClick={() => setIsMobileMenuOpen(true)}
              className="lg:hidden text-gray-500 hover:text-gray-700 focus:outline-none mr-4"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div className="hidden lg:block text-xl font-semibold text-gray-800">
              {/* Dynamic title could go here */}
            </div>
          </div>

          <div className="flex items-center flex-1 justify-end max-w-md">
            <form onSubmit={handleSearch} className="w-full relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Search materials, codes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-gray-50 placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors"
              />
            </form>
          </div>
        </header>

        {/* Main Area */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-4 lg:p-8">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 p-4 text-center text-xs text-gray-500">
          <p>SIH 2026 | PS-26099 | Synthetic Demo Data</p>
        </footer>
      </div>
    </div>
  );
};

export default Layout;
