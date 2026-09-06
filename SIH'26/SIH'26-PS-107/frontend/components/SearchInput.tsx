// components/SearchInput.tsx
import React from 'react';
import { FiSearch } from 'react-icons/fi';

interface SearchInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  placeholder?: string;
}

export const SearchInput: React.FC<SearchInputProps> = ({ placeholder = 'Search…', className = '', ...rest }) => (
  <div className="relative flex items-center">
    <FiSearch className="absolute left-3 text-gray-400" />
    <input
      type="search"
      placeholder={placeholder}
      className={`w-full pl-10 pr-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary/30 ${className}`}
      {...rest}
    />
  </div>
);
