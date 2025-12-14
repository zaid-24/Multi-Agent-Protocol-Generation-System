import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { useNavigate } from 'react-router-dom';
import { StatsChart } from '../components/StatsChart';
import {
  Button,
  Card,
  CardHeader,
  StatusBadge,
  LoadingState,
  EmptyState,
  DocumentEmptyIcon,
  PlusIcon,
  ClockIcon,
  LightningIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  ExclamationCircleIcon,
} from '../components/ui';

interface Session {
  session_id: string;
  status: string;
  created_at: string | null;
}

const INITIAL_DISPLAY_COUNT = 10;

const fetchSessions = async (): Promise<Session[]> => {
  const response = await apiClient.get<Session[]>('/sessions');
  return response.data;
};

export const SessionsPage: React.FC = () => {
  const [intent, setIntent] = useState('');
  const [context, setContext] = useState('');
  const [showAll, setShowAll] = useState(false);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: sessions, isLoading, error } = useQuery({
    queryKey: ['sessions'],
    queryFn: fetchSessions
  });

  const createMutation = useMutation({
    mutationFn: (data: { intent: string, context?: string }) => 
      apiClient.post('/sessions', { user_intent: data.intent, user_context: data.context }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      navigate(`/sessions/${data.data.session_id}`);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!intent) return;
    createMutation.mutate({ intent, context });
  };

  const displayedSessions = showAll 
    ? sessions 
    : sessions?.slice(0, INITIAL_DISPLAY_COUNT);
  const hasMore = (sessions?.length || 0) > INITIAL_DISPLAY_COUNT;
  const hiddenCount = (sessions?.length || 0) - INITIAL_DISPLAY_COUNT;

  return (
    <div className="content-container space-y-6">
      {/* ========== CREATE FORM ========== */}
      <Card>
        <CardHeader 
          title="Start New Protocol Design" 
          icon={<PlusIcon className="w-5 h-5 text-primary-500" />}
        />
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Intent Field */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Intent <span className="text-red-500">*</span>
            </label>
            <input 
              type="text" 
              className="input"
              placeholder="e.g., Create a CBT exposure hierarchy for social anxiety"
              value={intent}
              onChange={(e) => setIntent(e.target.value)}
              required
            />
            <p className="mt-1.5 text-xs text-gray-400">
              Describe the CBT protocol you want the agents to design
            </p>
          </div>

          {/* Context Field */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Clinical Context <span className="text-gray-400 font-normal">(Optional)</span>
            </label>
            <textarea 
              className="input resize-none"
              placeholder="e.g., Patient is a 28-year-old with moderate social anxiety, particularly around public speaking. No history of panic disorder."
              value={context}
              onChange={(e) => setContext(e.target.value)}
              rows={3}
            />
            <p className="mt-1.5 text-xs text-gray-400">
              Additional context helps agents create more tailored protocols
            </p>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end pt-2">
            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={createMutation.isPending}
              className="w-full sm:w-auto"
            >
              {createMutation.isPending ? 'Agents Working...' : (
                <>
                  <LightningIcon />
                  Start Session
                </>
              )}
            </Button>
          </div>
        </form>
      </Card>

      {/* ========== STATS CHART ========== */}
      <StatsChart sessions={sessions} />

      {/* ========== SESSIONS TABLE ========== */}
      <Card padding="none">
        <div className="p-6 pb-0">
          <CardHeader 
            title="Recent Sessions" 
            icon={<ClockIcon className="w-5 h-5 text-gray-400" />}
            action={
              sessions && sessions.length > 0 && (
                <span className="text-xs text-gray-400 font-medium">
                  {sessions.length} session{sessions.length !== 1 ? 's' : ''}
                </span>
              )
            }
          />
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="p-6">
            <LoadingState message="Loading sessions..." />
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="p-6">
            <div className="flex items-center justify-center py-8 text-red-600">
              <ExclamationCircleIcon className="w-5 h-5 mr-2" />
              Error loading sessions. Please try again.
            </div>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && sessions?.length === 0 && (
          <div className="p-6">
            <EmptyState
              icon={<DocumentEmptyIcon />}
              title="No sessions yet"
              description="Create your first CBT protocol above to get started!"
            />
          </div>
        )}

        {/* Sessions Table */}
        {!isLoading && !error && sessions && sessions.length > 0 && (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-y border-gray-100 bg-gray-50/50">
                    <th className="px-3 sm:px-6 py-2 sm:py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      Session
                    </th>
                    <th className="px-3 sm:px-6 py-2 sm:py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="hidden sm:table-cell px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-3 sm:px-6 py-2 sm:py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      <span className="sr-only">Action</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {displayedSessions?.map((session, index) => (
                    <SessionRow 
                      key={session.session_id}
                      session={session}
                      isEven={index % 2 === 0}
                      onClick={() => navigate(`/sessions/${session.session_id}`)}
                    />
                  ))}
                </tbody>
              </table>
            </div>
            
            {/* Expand/Collapse Button */}
            {hasMore && (
              <div className="p-4 border-t border-gray-100 text-center bg-gray-50/50">
                <Button
                  variant="subtle"
                  size="sm"
                  onClick={() => setShowAll(!showAll)}
                >
                  {showAll ? (
                    <>
                      Show Less
                      <ChevronUpIcon />
                    </>
                  ) : (
                    <>
                      Show {hiddenCount} More
                      <ChevronDownIcon />
                    </>
                  )}
                </Button>
              </div>
            )}
          </>
        )}
      </Card>
    </div>
  );
};

// ========== SESSION ROW COMPONENT ==========
interface SessionRowProps {
  session: Session;
  isEven: boolean;
  onClick: () => void;
}

const SessionRow: React.FC<SessionRowProps> = ({ session, isEven, onClick }) => (
  <tr 
    className={`
      hover:bg-blue-50/50 active:bg-blue-100/50 transition-colors cursor-pointer group touch-manipulation
      ${isEven ? 'bg-white' : 'bg-gray-50/30'}
    `}
    onClick={onClick}
  >
    <td className="px-3 sm:px-6 py-3 sm:py-4 whitespace-nowrap">
      <code className="text-xs sm:text-sm font-mono text-gray-600 bg-gray-100 px-1.5 sm:px-2 py-0.5 sm:py-1 rounded">
        {session.session_id.slice(0, 8)}
      </code>
    </td>
    <td className="px-3 sm:px-6 py-3 sm:py-4 whitespace-nowrap text-center">
      <StatusBadge status={session.status} size="sm" />
    </td>
    <td className="hidden sm:table-cell px-6 py-4 whitespace-nowrap text-sm text-gray-500">
      {session.created_at 
        ? new Date(session.created_at).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })
        : '—'
      }
    </td>
    <td className="px-3 sm:px-6 py-3 sm:py-4 whitespace-nowrap text-right">
      <span className="text-xs sm:text-sm text-primary-600 group-hover:text-primary-800 font-medium transition-colors inline-flex items-center gap-1">
        <span className="hidden sm:inline">View</span>
        <ChevronRightIcon className="w-4 h-4 transform group-hover:translate-x-0.5 transition-transform" />
      </span>
    </td>
  </tr>
);
