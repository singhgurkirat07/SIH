// components/Layout.tsx
import React, { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="flex h-screen w-screen bg-gray-100 text-gray-900 font-sans overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 h-full overflow-hidden">
        <TopBar />
        <div className="bg-amber-50 border-b border-amber-200 px-6 py-1.5 flex justify-center items-center text-xs text-amber-800">
          <span className="font-semibold uppercase mr-2 tracking-wide">System Notice:</span>
          Information is generated from available BIS source material. Official BIS publications and portals remain authoritative.
        </div>
        <main className="flex-1 overflow-hidden relative">
          {children}
        </main>
      </div>
    </div>
  );
}
