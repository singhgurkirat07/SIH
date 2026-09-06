// components/TwoColumnLayout.tsx
import React from 'react';

interface TwoColumnLayoutProps {
  left: React.ReactNode;
  right: React.ReactNode;
}

export const TwoColumnLayout: React.FC<TwoColumnLayoutProps> = ({ left, right }) => (
  <div className="flex h-full border-t border-gray-300">
    <section className="w-1/2 border-r border-gray-300 bg-white overflow-y-auto">{left}</section>
    <section className="w-1/2 bg-gray-50 overflow-y-auto">{right}</section>
  </div>
);
