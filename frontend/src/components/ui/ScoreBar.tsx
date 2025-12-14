import React from 'react';

type ColorScheme = 'green' | 'purple' | 'blue' | 'amber' | 'red';

interface ScoreBarProps {
  label: string;
  score: number | null | undefined;
  color: ColorScheme;
  showDot?: boolean;
}

const COLOR_CLASSES: Record<ColorScheme, { bar: string; text: string; dot: string }> = {
  green: { bar: 'bg-green-500', text: 'text-green-600', dot: 'bg-green-500' },
  purple: { bar: 'bg-purple-500', text: 'text-purple-600', dot: 'bg-purple-500' },
  blue: { bar: 'bg-blue-500', text: 'text-blue-600', dot: 'bg-blue-500' },
  amber: { bar: 'bg-amber-500', text: 'text-amber-600', dot: 'bg-amber-500' },
  red: { bar: 'bg-red-500', text: 'text-red-600', dot: 'bg-red-500' },
};

/**
 * Displays a labeled score with a progress bar and numeric value.
 * Used for displaying Safety, Empathy, Clinical scores etc.
 */
export const ScoreBar: React.FC<ScoreBarProps> = ({ 
  label, 
  score, 
  color,
  showDot = true 
}) => {
  const colors = COLOR_CLASSES[color];
  const value = score ?? 0;

  return (
    <div className="flex items-center gap-3">
      {showDot && (
        <span className={`w-2 h-2 rounded-full flex-shrink-0 ${colors.dot}`} />
      )}
      <span className="text-sm text-gray-600 flex-1">{label}</span>
      <div className="flex items-center gap-2">
        <div className="w-20 h-2 bg-gray-100 rounded-full overflow-hidden">
          <div 
            className={`h-full ${colors.bar} rounded-full transition-all duration-500`}
            style={{ width: `${value * 100}%` }}
          />
        </div>
        <span className={`text-sm font-bold ${colors.text} w-12 text-right font-mono`}>
          {score?.toFixed(2) ?? '—'}
        </span>
      </div>
    </div>
  );
};

interface ScoreGroupProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Container for grouping multiple ScoreBars with consistent spacing.
 */
export const ScoreGroup: React.FC<ScoreGroupProps> = ({ children, className = '' }) => (
  <div className={`bg-gray-50 rounded-lg p-4 space-y-3 ${className}`}>
    {children}
  </div>
);
