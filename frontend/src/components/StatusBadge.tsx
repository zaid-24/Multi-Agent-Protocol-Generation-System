import React from 'react';

type StatusType = 'APPROVED' | 'FAILED' | 'REJECTED' | 'AWAITING_HUMAN' | 'DRAFTING' | 'REVIEWING' | 'REVISING' | 'INIT' | string;

interface StatusBadgeProps {
  status: StatusType;
  size?: 'sm' | 'md';
}

const STATUS_CONFIG: Record<string, { bg: string; text: string; icon?: string }> = {
  APPROVED: { 
    bg: 'bg-green-100', 
    text: 'text-green-700',
  },
  FAILED: { 
    bg: 'bg-red-100', 
    text: 'text-red-700',
  },
  REJECTED: { 
    bg: 'bg-orange-100', 
    text: 'text-orange-700',
  },
  AWAITING_HUMAN: { 
    bg: 'bg-blue-100', 
    text: 'text-blue-700',
  },
  DRAFTING: { 
    bg: 'bg-yellow-100', 
    text: 'text-yellow-700',
  },
  REVIEWING: { 
    bg: 'bg-purple-100', 
    text: 'text-purple-700',
  },
  REVISING: { 
    bg: 'bg-amber-100', 
    text: 'text-amber-700',
  },
  INIT: { 
    bg: 'bg-gray-100', 
    text: 'text-gray-600',
  },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const config = STATUS_CONFIG[status] || { bg: 'bg-gray-100', text: 'text-gray-600' };
  
  const sizeClasses = {
    sm: 'px-1.5 py-0.5 text-[10px] gap-1',
    md: 'px-2.5 py-1 text-xs gap-1.5',
  };

  const dotSizes = {
    sm: 'w-1 h-1',
    md: 'w-1.5 h-1.5',
  };

  // Convert text color to background color for dot
  const dotColor = config.text
    .replace('text-', 'bg-')
    .replace('-700', '-500')
    .replace('-600', '-400');

  return (
    <span 
      className={`
        inline-flex items-center font-semibold rounded-full whitespace-nowrap
        ${config.bg} ${config.text} ${sizeClasses[size]}
      `}
    >
      <span className={`rounded-full flex-shrink-0 ${dotSizes[size]} ${dotColor}`} />
      <span className="truncate max-w-[80px] sm:max-w-none">
        {status.replace('_', ' ')}
      </span>
    </span>
  );
};
