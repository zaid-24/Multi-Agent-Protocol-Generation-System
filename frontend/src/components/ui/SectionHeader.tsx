import React from 'react';

interface SectionHeaderProps {
  title: string;
  className?: string;
}

/**
 * A consistent section header with uppercase styling.
 * Used for sidebar sections like "Status", "Progress", "Scores".
 */
export const SectionHeader: React.FC<SectionHeaderProps> = ({ title, className = '' }) => (
  <h3 className={`text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 ${className}`}>
    {title}
  </h3>
);

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

/**
 * A page-level header with title, optional subtitle, icon, and action.
 */
export const PageHeader: React.FC<PageHeaderProps> = ({ title, subtitle, icon, action }) => (
  <div className="flex items-start justify-between mb-6">
    <div className="flex items-center gap-3">
      {icon && (
        <div className="p-2 rounded-lg bg-primary-100 text-primary-600">
          {icon}
        </div>
      )}
      <div>
        <h1 className="text-xl font-bold text-gray-900">{title}</h1>
        {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
      </div>
    </div>
    {action && <div>{action}</div>}
  </div>
);
