// components/Stepper.tsx
import React from 'react';

interface StepperProps {
  steps: string[]; // step titles
  current: number; // index of current step (0‑based)
}

export const Stepper: React.FC<StepperProps> = ({ steps, current }) => (
  <nav className="flex items-center space-x-4 mb-6">
    {steps.map((label, idx) => (
      <div key={idx} className="flex items-center">
        <div
          className={`w-8 h-8 flex items-center justify-center rounded-full text-sm font-medium 
            ${idx < current ? 'bg-primary text-white' : idx === current ? 'bg-primary/20 text-primary' : 'bg-gray-200 text-gray-500'}`}
        >
          {idx + 1}
        </div>
        <span className={`ml-2 text-sm ${idx < current ? 'text-primary font-semibold' : 'text-gray-500'}`}>{label}</span>
        {idx < steps.length - 1 && <span className="mx-2 text-gray-300">—</span>}
      </div>
    ))}
  </nav>
);
