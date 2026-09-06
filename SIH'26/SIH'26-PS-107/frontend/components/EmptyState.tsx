// components/EmptyState.tsx
import React from 'react';
import { FiDatabase } from 'react-icons/fi';

interface EmptyStateProps {
  title: string;
  description?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ title, description }) => (
  <div className="flex flex-col items-center justify-center p-10 border border-dashed border-gray-300 bg-gray-50 text-center">
    <div className="bg-white p-3 rounded shadow-sm border border-gray-200 mb-4">
      <FiDatabase className="text-2xl text-gray-400" />
    </div>
    <h3 className="text-base font-bold text-gray-800 mb-1 tracking-tight">{title}</h3>
    {description && <p className="text-sm text-gray-500 max-w-sm leading-relaxed">{description}</p>}
  </div>
);
