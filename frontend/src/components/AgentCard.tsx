import React, { useState } from 'react';

interface AgentCardProps {
  name: string;
  subtitle: string;
  score: number;
  summary?: string;
  rationale?: string;
  colorScheme: 'green' | 'purple' | 'blue';
  icon: React.ReactNode;
}

const COLOR_SCHEMES = {
  green: {
    bg: 'bg-gradient-to-br from-green-50 to-emerald-50',
    border: 'border-green-200',
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600',
    scoreBg: 'bg-green-600',
    scoreText: 'text-white',
    accentBar: 'bg-green-500',
    buttonText: 'text-green-600 hover:text-green-800',
  },
  purple: {
    bg: 'bg-gradient-to-br from-purple-50 to-violet-50',
    border: 'border-purple-200',
    iconBg: 'bg-purple-100',
    iconColor: 'text-purple-600',
    scoreBg: 'bg-purple-600',
    scoreText: 'text-white',
    accentBar: 'bg-purple-500',
    buttonText: 'text-purple-600 hover:text-purple-800',
  },
  blue: {
    bg: 'bg-gradient-to-br from-blue-50 to-indigo-50',
    border: 'border-blue-200',
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    scoreBg: 'bg-blue-600',
    scoreText: 'text-white',
    accentBar: 'bg-blue-500',
    buttonText: 'text-blue-600 hover:text-blue-800',
  },
};

export const AgentCard: React.FC<AgentCardProps> = ({
  name,
  subtitle,
  score,
  summary,
  rationale,
  colorScheme,
  icon,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const colors = COLOR_SCHEMES[colorScheme];
  const scorePercent = Math.round(score * 100);
  const isGoodScore = score >= 0.6;

  // Check if text is long enough to need expansion
  const hasLongText = (summary && summary.length > 80) || (rationale && rationale.length > 100);

  return (
    <div className={`relative overflow-hidden rounded-xl border ${colors.border} ${colors.bg}`}>
      {/* Accent bar */}
      <div className={`absolute top-0 left-0 right-0 h-1 ${colors.accentBar}`} />
      
      <div className="p-4 pt-5">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg ${colors.iconBg} ${colors.iconColor} flex items-center justify-center flex-shrink-0`}>
              {icon}
            </div>
            <div className="min-w-0">
              <h3 className="font-semibold text-gray-900 text-sm">{name}</h3>
              <p className="text-xs text-gray-500">{subtitle}</p>
            </div>
          </div>
          
          {/* Score Badge */}
          <div className={`${colors.scoreBg} ${colors.scoreText} px-3 py-1.5 rounded-lg text-center min-w-[52px] flex-shrink-0`}>
            <div className="text-lg font-bold leading-none">{scorePercent}</div>
            <div className="text-[10px] opacity-80">/ 100</div>
          </div>
        </div>

        {/* Summary */}
        {summary && (
          <div className="mb-2">
            <p className={`text-xs text-gray-600 italic ${isExpanded ? '' : 'line-clamp-2'}`}>
              "{summary}"
            </p>
          </div>
        )}

        {/* Rationale */}
        {rationale && (
          <p className={`text-xs text-gray-700 ${isExpanded ? '' : 'line-clamp-2'}`}>
            {rationale}
          </p>
        )}

        {/* Read More / Show Less Button */}
        {hasLongText && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className={`mt-2 text-xs font-medium ${colors.buttonText} transition-colors focus:outline-none focus-visible:underline`}
          >
            {isExpanded ? (
              <span className="inline-flex items-center gap-1">
                Show Less
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                </svg>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1">
                Read More
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </span>
            )}
          </button>
        )}

        {/* Score indicator bar */}
        <div className="mt-3 pt-3 border-t border-gray-200/50">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-gray-500">Score</span>
            <span className={`font-medium ${isGoodScore ? 'text-green-600' : 'text-amber-600'}`}>
              {isGoodScore ? 'Passing' : 'Needs Work'}
            </span>
          </div>
          <div className="h-1.5 bg-white/80 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-500 ${isGoodScore ? 'bg-green-500' : 'bg-amber-500'}`}
              style={{ width: `${scorePercent}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// Agent-specific icons
export const SafetyIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
  </svg>
);

export const EmpathyIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
  </svg>
);

export const ClinicalIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
  </svg>
);
