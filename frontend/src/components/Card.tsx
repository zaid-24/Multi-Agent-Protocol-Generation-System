import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
}

const PADDING_CLASSES = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  padding = 'md',
  hover = false,
}) => {
  return (
    <div
      className={`
        bg-white rounded-xl border border-gray-100/80 shadow-sm
        ${hover ? 'transition-shadow duration-200 hover:shadow-md' : ''}
        ${PADDING_CLASSES[padding]}
        ${className}
      `}
    >
      {children}
    </div>
  );
};

interface CardHeaderProps {
  title: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export const CardHeader: React.FC<CardHeaderProps> = ({ title, icon, action }) => {
  return (
    <div className="flex items-center justify-between mb-4">
      <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
        {icon}
        {title}
      </h2>
      {action}
    </div>
  );
};
