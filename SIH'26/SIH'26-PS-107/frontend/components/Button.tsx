// components/Button.tsx
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline';
}

const variantClasses = {
  primary: 'bg-primary text-white hover:bg-primary/90',
  secondary: 'bg-accent text-white hover:bg-accent/90',
  outline: 'border border-primary text-primary hover:bg-primary/10',
};

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  className = '',
  ...rest
}) => {
  return (
    <button
      className={`px-4 py-2 rounded ${variantClasses[variant]} ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
};
