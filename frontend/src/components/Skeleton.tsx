import React from 'react';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = '',
  variant = 'rectangular',
  width,
  height,
}) => {
  const variantClasses = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  };

  return (
    <div
      className={`animate-pulse bg-gray-200 ${variantClasses[variant]} ${className}`}
      style={{ width, height }}
    />
  );
};

// Skeleton compositions for common use cases
export const SkeletonCard: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`bg-white rounded-xl border border-gray-100 p-4 ${className}`}>
    <div className="flex items-center gap-3 mb-3">
      <Skeleton variant="circular" width={40} height={40} />
      <div className="flex-1">
        <Skeleton width="60%" height={16} className="mb-2" />
        <Skeleton width="40%" height={12} />
      </div>
    </div>
    <Skeleton width="100%" height={12} className="mb-2" />
    <Skeleton width="80%" height={12} />
  </div>
);

export const SkeletonText: React.FC<{ lines?: number; className?: string }> = ({ 
  lines = 3, 
  className = '' 
}) => (
  <div className={`space-y-2 ${className}`}>
    {Array.from({ length: lines }).map((_, i) => (
      <Skeleton 
        key={i} 
        width={i === lines - 1 ? '60%' : '100%'} 
        height={14} 
        variant="text"
      />
    ))}
  </div>
);

// Session Detail specific skeletons
export const SessionDetailSkeleton: React.FC = () => (
  <div className="flex min-h-[calc(100vh-140px)] -my-8 bg-gray-50">
    {/* Left Sidebar Skeleton */}
    <div className="w-72 bg-white border-r border-gray-200 p-6 flex-shrink-0">
      <Skeleton width={100} height={16} className="mb-8" />
      
      {/* Status */}
      <Skeleton width={80} height={12} className="mb-3" />
      <Skeleton width={120} height={32} variant="rectangular" className="rounded-full mb-8" />
      
      {/* Metrics */}
      <Skeleton width={80} height={12} className="mb-3" />
      <div className="space-y-3 mb-8">
        {[1, 2].map(i => (
          <div key={i} className="flex justify-between">
            <Skeleton width={60} height={14} />
            <Skeleton width={40} height={14} />
          </div>
        ))}
      </div>
      
      {/* Scores */}
      <Skeleton width={60} height={12} className="mb-3" />
      <div className="space-y-3">
        {[1, 2, 3].map(i => (
          <div key={i} className="flex justify-between items-center">
            <Skeleton width={50} height={14} />
            <div className="flex items-center gap-2">
              <Skeleton width={64} height={6} className="rounded-full" />
              <Skeleton width={36} height={14} />
            </div>
          </div>
        ))}
      </div>
    </div>

    {/* Center Content Skeleton */}
    <div className="flex-1 p-8">
      <div className="max-w-3xl mx-auto">
        <Skeleton width={200} height={24} className="mb-2" />
        <Skeleton width={300} height={16} className="mb-6" />
        
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 min-h-[500px]">
          <SkeletonText lines={12} />
        </div>
      </div>
    </div>

    {/* Right Sidebar Skeleton */}
    <div className="w-80 bg-white border-l border-gray-200 p-6 flex-shrink-0">
      <Skeleton width={120} height={12} className="mb-6" />
      
      <div className="space-y-4">
        {[1, 2, 3].map(i => (
          <SkeletonCard key={i} />
        ))}
      </div>
    </div>
  </div>
);
