// components/Input.tsx
import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const Input: React.FC<InputProps> = ({ label, className = '', ...rest }) => (
  <div className="flex flex-col space-y-1">
    {label && <label className="text-sm font-medium text-primary">{label}</label>}
    <input
      className={`border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/30 ${className}`}
      {...rest}
    />
  </div>
);
