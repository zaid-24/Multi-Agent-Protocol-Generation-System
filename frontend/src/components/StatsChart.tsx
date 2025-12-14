import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface Session {
  session_id: string;
  status: string;
  created_at: string | null;
}

interface StatsChartProps {
  sessions: Session[] | undefined;
}

// Status colors matching the app's design system (using Tailwind theme colors)
const STATUS_COLORS: Record<string, { fill: string; bg: string; text: string }> = {
  APPROVED: { fill: '#16a34a', bg: 'bg-safe-100', text: 'text-safe-700' },
  AWAITING_HUMAN: { fill: '#2563eb', bg: 'bg-primary-100', text: 'text-primary-700' },
  FAILED: { fill: '#dc2626', bg: 'bg-danger-100', text: 'text-danger-700' },
  REJECTED: { fill: '#ea580c', bg: 'bg-orange-100', text: 'text-orange-700' },
};

const TRACKED_STATUSES = ['APPROVED', 'AWAITING_HUMAN', 'FAILED', 'REJECTED'];

export const StatsChart: React.FC<StatsChartProps> = ({ sessions }) => {
  // Compute counts for each tracked status
  const statusCounts = TRACKED_STATUSES.map((status) => ({
    status: status === 'AWAITING_HUMAN' ? 'AWAITING' : status,
    fullStatus: status,
    count: sessions?.filter((s) => s.status === status).length || 0,
  }));

  const totalCount = statusCounts.reduce((sum, item) => sum + item.count, 0);
  const totalSessions = sessions?.length || 0;

  // No data state
  if (!sessions || sessions.length === 0 || totalCount === 0) {
    return (
      <div className="card p-6">
        <h2 className="section-title flex items-center gap-2">
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Session Overview
        </h2>
        <div className="flex items-center justify-center h-20 text-gray-400 text-sm">
          <svg className="w-5 h-5 mr-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          No sessions to summarize yet
        </div>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="section-title mb-0 flex items-center gap-2">
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Session Overview
        </h2>
        <span className="text-xs text-gray-400 font-medium">
          {totalSessions} total session{totalSessions !== 1 ? 's' : ''}
        </span>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
        {statusCounts.map((item) => (
          <div 
            key={item.fullStatus} 
            className={`rounded-lg p-3 ${STATUS_COLORS[item.fullStatus]?.bg || 'bg-gray-100'}`}
          >
            <div className={`text-2xl font-bold ${STATUS_COLORS[item.fullStatus]?.text || 'text-gray-700'}`}>
              {item.count}
            </div>
            <div className="text-xs text-gray-600 font-medium truncate">
              {item.status}
            </div>
          </div>
        ))}
      </div>

      {/* Bar Chart */}
      <div className="h-32 mt-2">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={statusCounts}
            margin={{ top: 5, right: 5, left: -20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" vertical={false} />
            <XAxis
              dataKey="status"
              tick={{ fontSize: 10, fill: '#9ca3af' }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              allowDecimals={false}
              tick={{ fontSize: 10, fill: '#9ca3af' }}
              axisLine={false}
              tickLine={false}
              width={25}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: 'none',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                fontSize: '12px',
                padding: '8px 12px',
              }}
              cursor={{ fill: 'rgba(0,0,0,0.02)' }}
              formatter={(value: number, _name: string, props: { payload: { fullStatus: string } }) => [
                value,
                props.payload.fullStatus,
              ]}
            />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {statusCounts.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={STATUS_COLORS[entry.fullStatus]?.fill || '#9ca3af'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
