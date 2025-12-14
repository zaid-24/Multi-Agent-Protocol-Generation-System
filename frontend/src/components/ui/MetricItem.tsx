import React from 'react';

interface MetricItemProps {
  label: string;
  value: string | number;
  suffix?: string;
  mono?: boolean;
}

/**
 * A simple row displaying a label and value, commonly used in sidebars/stats.
 */
export const MetricItem: React.FC<MetricItemProps> = ({ 
  label, 
  value, 
  suffix,
  mono = true 
}) => (
  <div className="flex justify-between items-center">
    <span className="text-sm text-gray-600">{label}</span>
    <span className={`text-sm font-bold text-gray-900 ${mono ? 'font-mono' : ''}`}>
      {value}
      {suffix && <span className="text-gray-400 font-normal"> {suffix}</span>}
    </span>
  </div>
);

interface MetricGroupProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Container for grouping multiple MetricItems with consistent spacing.
 */
export const MetricGroup: React.FC<MetricGroupProps> = ({ children, className = '' }) => (
  <div className={`bg-gray-50 rounded-lg p-4 space-y-3 ${className}`}>
    {children}
  </div>
);
