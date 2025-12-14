import React from 'react';

interface ProgressBarProps {
  value: number;
  max: number;
  color?: 'primary' | 'green' | 'blue' | 'amber' | 'red';
  size?: 'sm' | 'md';
  showLabel?: boolean;
  className?: string;
}

const COLOR_CLASSES = {
  primary: 'bg-primary-500',
  green: 'bg-green-500',
  blue: 'bg-blue-500',
  amber: 'bg-amber-500',
  red: 'bg-red-500',
};

const SIZE_CLASSES = {
  sm: 'h-1.5',
  md: 'h-2',
};

/**
 * A simple progress bar component.
 */
export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max,
  color = 'primary',
  size = 'md',
  showLabel = false,
  className = '',
}) => {
  const percentage = max > 0 ? (value / max) * 100 : 0;

  return (
    <div className={className}>
      {showLabel && (
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>{value}</span>
          <span>{max}</span>
        </div>
      )}
      <div className={`bg-gray-200 rounded-full overflow-hidden ${SIZE_CLASSES[size]}`}>
        <div 
          className={`${COLOR_CLASSES[color]} rounded-full transition-all duration-500 h-full`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
