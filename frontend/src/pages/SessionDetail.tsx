import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getSessionState, humanApprove } from '../api/sessions';
import type { Review } from '../api/sessions';
import { AgentCard } from '../components/AgentCard';
import {
  Button,
  StatusBadge,
  SessionDetailSkeleton,
  SectionHeader,
  MetricItem,
  MetricGroup,
  ScoreBar,
  ScoreGroup,
  ProgressBar,
  EmptyState,
  ChatEmptyIcon,
  BackIcon,
  DocumentIcon,
  SpinnerIcon,
  EditIcon,
  SafetyIcon,
  EmpathyIcon,
  ClinicalIcon,
  ExclamationCircleIcon,
} from '../components/ui';

export const SessionDetail: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [draftContent, setDraftContent] = useState('');
  const [comments, setComments] = useState('');

  const { data: state, isLoading, error } = useQuery({
    queryKey: ['session', sessionId],
    queryFn: () => getSessionState(sessionId!),
    enabled: !!sessionId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === 'APPROVED' || status === 'FAILED' || status === 'REJECTED' || status === 'AWAITING_HUMAN') return false;
      return 2000;
    }
  });

  useEffect(() => {
    if (state?.current_draft) {
      if (state.status !== 'AWAITING_HUMAN' || !draftContent) {
        setDraftContent(state.current_draft.content);
      }
    }
  }, [state?.current_draft?.id, state?.status]);

  const approveMutation = useMutation({
    mutationFn: (data: { action: "APPROVE_FINAL" | "APPROVE_CONTINUE" | "REQUEST_REVISION" | "REJECT" }) => 
      humanApprove(sessionId!, draftContent, data.action, comments),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['session', sessionId] });
      setComments('');
    },
    onError: (err) => {
      alert('Action failed: ' + String(err));
    }
  });

  // Loading state with skeleton
  if (isLoading) {
    return <SessionDetailSkeleton />;
  }

  // Error state
  if (error) {
    return (
      <div className="content-container py-12">
        <div className="max-w-md mx-auto text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
            <ExclamationCircleIcon className="w-8 h-8 text-red-500" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Session</h2>
          <p className="text-gray-500 mb-6">{String(error)}</p>
          <Button variant="secondary" onClick={() => navigate('/sessions')}>
            <BackIcon /> Back to Sessions
          </Button>
        </div>
      </div>
    );
  }

  // No state
  if (!state) {
    return (
      <div className="content-container py-12">
        <div className="max-w-md mx-auto text-center">
          <p className="text-gray-500 mb-6">No session state found.</p>
          <Button variant="secondary" onClick={() => navigate('/sessions')}>
            <BackIcon /> Back to Sessions
          </Button>
        </div>
      </div>
    );
  }

  const isAwaitingHuman = state.status === 'AWAITING_HUMAN';
  const isTerminal = ['APPROVED', 'FAILED', 'REJECTED'].includes(state.status);
  const draftCount = state.draft_history.length + (state.current_draft ? 1 : 0);

  // Group reviews by agent
  const latestReviews: Record<string, Review> = {};
  state.reviews.forEach(r => {
    latestReviews[r.agent_name] = r;
  });

  return (
    <div className="flex flex-col lg:flex-row min-h-[calc(100vh-80px)] bg-gray-50">
      {/* ========== LEFT SIDEBAR (hidden on mobile, shows as top bar) ========== */}
      <LeftSidebar
        status={state.status}
        iteration={state.iteration}
        maxIterations={state.max_iterations}
        draftCount={draftCount}
        safetyScore={state.safety_score}
        empathyScore={state.empathy_score}
        clinicalScore={state.clinical_score}
        sessionId={sessionId}
        isTerminal={isTerminal}
        isAwaitingHuman={isAwaitingHuman}
        onBack={() => navigate('/sessions')}
      />

      {/* ========== CENTER CONTENT ========== */}
      <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto">
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <div className="mb-4 sm:mb-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-primary-100 text-primary-600 flex-shrink-0">
                <DocumentIcon />
              </div>
              <div className="min-w-0">
                <h1 className="text-lg sm:text-xl font-bold text-gray-900">Protocol Draft</h1>
                <p className="text-xs sm:text-sm text-gray-500 truncate">Review and approve the generated CBT protocol</p>
              </div>
            </div>
          </div>

          {/* Intent Card */}
          <IntentCard 
            intent={state.user_intent} 
            context={state.user_context} 
          />

          {/* Draft Document Card */}
          <DraftDocumentCard
            currentDraft={state.current_draft}
            isAwaitingHuman={isAwaitingHuman}
            isTerminal={isTerminal}
            status={state.status}
            draftContent={draftContent}
            comments={comments}
            isPending={approveMutation.isPending}
            onDraftChange={setDraftContent}
            onCommentsChange={setComments}
            onAction={(action) => approveMutation.mutate({ action })}
          />
        </div>
      </main>

      {/* ========== RIGHT SIDEBAR (Agent Board) - scrolls on mobile ========== */}
      <AgentBoardSidebar 
        latestReviews={latestReviews}
        scratchpadNotes={state.scratchpads?.notes?.['DraftingAgent']}
      />
    </div>
  );
};

// ========== LEFT SIDEBAR ==========
interface LeftSidebarProps {
  status: string;
  iteration: number;
  maxIterations: number;
  draftCount: number;
  safetyScore: number | null | undefined;
  empathyScore: number | null | undefined;
  clinicalScore: number | null | undefined;
  sessionId: string | undefined;
  isTerminal: boolean;
  isAwaitingHuman: boolean;
  onBack: () => void;
}

const LeftSidebar: React.FC<LeftSidebarProps> = ({
  status,
  iteration,
  maxIterations,
  draftCount,
  safetyScore,
  empathyScore,
  clinicalScore,
  sessionId,
  isTerminal,
  isAwaitingHuman,
  onBack,
}) => (
  <aside className="w-full lg:w-72 bg-white border-b lg:border-b-0 lg:border-r border-gray-200 flex-shrink-0 flex flex-col">
    {/* Back Button - Always visible and prominent */}
    <div className="p-4 border-b border-gray-200 bg-gray-50/50">
      <button 
        onClick={onBack}
        className="flex items-center gap-2 text-sm text-primary-600 hover:text-primary-800 active:text-primary-900 transition-colors font-medium touch-manipulation group"
      >
        <span className="w-6 h-6 rounded-full bg-primary-100 flex items-center justify-center group-hover:bg-primary-200 transition-colors">
          <BackIcon />
        </span>
        <span>Back to Sessions</span>
      </button>
    </div>

    {/* Mobile: Horizontal scroll layout, Desktop: Vertical */}
    <div className="flex-1 p-4 lg:p-5 overflow-y-auto">
      {/* Mobile compact view */}
      <div className="flex flex-wrap gap-4 lg:block lg:space-y-0">
        {/* Status Section */}
        <div className="lg:mb-8">
          <SectionHeader title="Status" />
          <div className="flex items-center gap-3">
            <StatusBadge status={status} />
            {!isTerminal && !isAwaitingHuman && (
              <SpinnerIcon className="w-5 h-5 animate-spin text-gray-400" />
            )}
          </div>
        </div>

        {/* Progress Section */}
        <div className="lg:mb-8 flex-1 min-w-[180px] lg:min-w-0">
          <SectionHeader title="Progress" />
          <MetricGroup>
            <MetricItem 
              label="Iteration" 
              value={iteration} 
              suffix={`/ ${maxIterations}`}
            />
            <MetricItem 
              label="Draft Versions" 
              value={draftCount} 
            />
            <div className="pt-2">
              <ProgressBar value={iteration} max={maxIterations} />
            </div>
          </MetricGroup>
        </div>

        {/* Scores Section */}
        <div className="flex-1 min-w-[200px] lg:min-w-0">
          <SectionHeader title="Quality Scores" />
          <ScoreGroup>
            <ScoreBar label="Safety" score={safetyScore} color="green" />
            <ScoreBar label="Empathy" score={empathyScore} color="purple" />
            <ScoreBar label="Clinical" score={clinicalScore} color="blue" />
          </ScoreGroup>
        </div>
      </div>
    </div>

    {/* Session ID Footer - hidden on mobile for cleaner look */}
    <div className="hidden lg:block p-4 border-t border-gray-100 bg-gray-50">
      <div className="text-xs text-gray-400">Session ID</div>
      <code className="text-xs font-mono text-gray-600 break-all">{sessionId?.slice(0, 16)}...</code>
    </div>
  </aside>
);

// ========== INTENT CARD ==========
interface IntentCardProps {
  intent: string;
  context?: string;
}

const IntentCard: React.FC<IntentCardProps> = ({ intent, context }) => (
  <div className="bg-gradient-to-r from-primary-50 to-blue-50 border border-primary-100 rounded-xl p-4 mb-6">
    <div className="text-xs font-semibold text-primary-600 uppercase tracking-wider mb-1">
      Original Intent
    </div>
    <p className="text-gray-800 font-medium">"{intent}"</p>
    {context && (
      <p className="text-sm text-gray-600 mt-2">{context}</p>
    )}
  </div>
);

// ========== DRAFT DOCUMENT CARD ==========
interface DraftDocumentCardProps {
  currentDraft: { content: string; version_number: number } | null;
  isAwaitingHuman: boolean;
  isTerminal: boolean;
  status: string;
  draftContent: string;
  comments: string;
  isPending: boolean;
  onDraftChange: (content: string) => void;
  onCommentsChange: (comments: string) => void;
  onAction: (action: "APPROVE_FINAL" | "APPROVE_CONTINUE" | "REQUEST_REVISION" | "REJECT") => void;
}

const DraftDocumentCard: React.FC<DraftDocumentCardProps> = ({
  currentDraft,
  isAwaitingHuman,
  isTerminal,
  status,
  draftContent,
  comments,
  isPending,
  onDraftChange,
  onCommentsChange,
  onAction,
}) => (
  <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
    {/* Document Header */}
    <div className="bg-gray-50 px-4 sm:px-6 py-3 border-b border-gray-200 flex items-center justify-between gap-2">
      <div className="flex items-center gap-2 text-sm text-gray-600 min-w-0">
        <DocumentIcon className="w-4 h-4 flex-shrink-0" />
        <span className="font-medium truncate">CBT Protocol Document</span>
      </div>
      {currentDraft && (
        <span className="text-xs text-gray-400 flex-shrink-0">
          v{currentDraft.version_number}
        </span>
      )}
    </div>

    {/* Document Content - with max height and scroll */}
    <div className="p-4 sm:p-6 min-h-[300px] max-h-[60vh] overflow-y-auto">
      {isAwaitingHuman ? (
        <textarea 
          className="w-full min-h-[280px] sm:min-h-[380px] p-3 sm:p-4 font-mono text-xs sm:text-sm text-gray-800 leading-relaxed bg-white border border-gray-200 rounded-lg resize-y focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
          value={draftContent}
          onChange={(e) => onDraftChange(e.target.value)}
          placeholder="Edit the protocol draft..."
        />
      ) : (
        <div className="whitespace-pre-wrap font-mono text-xs sm:text-sm text-gray-800 leading-relaxed break-words">
          {currentDraft?.content || (
            <div className="flex flex-col items-center justify-center py-12 sm:py-16 text-gray-400">
              <svg className="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <SpinnerIcon className="w-5 h-5 animate-spin" />
              <p className="mt-3 text-sm text-center">Agents are generating your protocol...</p>
            </div>
          )}
        </div>
      )}
    </div>

    {/* Action Bar - responsive layout */}
    {isAwaitingHuman && (
      <div className="bg-gray-50 border-t border-gray-200 p-4 sm:p-6">
        {/* Feedback Input */}
        <div className="mb-4 sm:mb-5">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Feedback Notes <span className="text-gray-400 font-normal">(Optional)</span>
          </label>
          <input 
            type="text"
            className="w-full px-3 sm:px-4 py-2.5 text-sm border border-gray-200 rounded-lg bg-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
            placeholder="Add comments for the agents..."
            value={comments}
            onChange={(e) => onCommentsChange(e.target.value)}
          />
        </div>

        {/* Action Buttons - stack on mobile */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <Button
            variant="danger"
            onClick={() => onAction("REJECT")}
            isLoading={isPending}
            disabled={isPending}
            className="order-last sm:order-first"
          >
            Reject
          </Button>

          <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
            <Button
              variant="secondary"
              onClick={() => onAction("REQUEST_REVISION")}
              isLoading={isPending}
              disabled={isPending}
            >
              Request Revision
            </Button>
            <Button
              variant="primary"
              onClick={() => onAction("APPROVE_CONTINUE")}
              isLoading={isPending}
              disabled={isPending}
            >
              Approve & Continue
            </Button>
            <Button
              variant="success"
              onClick={() => onAction("APPROVE_FINAL")}
              isLoading={isPending}
              disabled={isPending}
            >
              ✓ Finalize
            </Button>
          </div>
        </div>
      </div>
    )}

    {/* Terminal State Banner */}
    {isTerminal && (
      <TerminalBanner status={status} />
    )}
  </div>
);

// ========== TERMINAL BANNER ==========
const TerminalBanner: React.FC<{ status: string }> = ({ status }) => {
  const config: Record<string, { bg: string; text: string; message: string }> = {
    APPROVED: { bg: 'bg-green-50', text: 'text-green-700', message: '✓ Protocol Approved' },
    REJECTED: { bg: 'bg-orange-50', text: 'text-orange-700', message: '✗ Protocol Rejected' },
    FAILED: { bg: 'bg-red-50', text: 'text-red-700', message: '✗ Protocol Failed (Max iterations reached)' },
  };
  const { bg, text, message } = config[status] || config.FAILED;

  return (
    <div className={`p-4 text-center ${bg} ${text}`}>
      <span className="font-medium">{message}</span>
    </div>
  );
};

// ========== AGENT BOARD SIDEBAR ==========
interface AgentBoardSidebarProps {
  latestReviews: Record<string, Review>;
  scratchpadNotes?: string;
}

const AgentBoardSidebar: React.FC<AgentBoardSidebarProps> = ({ 
  latestReviews, 
  scratchpadNotes 
}) => (
  <aside className="w-full lg:w-80 bg-gray-50 border-t lg:border-t-0 lg:border-l border-gray-200 flex-shrink-0 overflow-y-auto max-h-[50vh] lg:max-h-none">
    <div className="p-4 sm:p-5">
      <SectionHeader title="Agent Evaluations" className="mb-4" />

      {/* Horizontal scroll on mobile, vertical on desktop */}
      <div className="flex lg:flex-col gap-4 overflow-x-auto lg:overflow-x-visible pb-2 lg:pb-0 -mx-4 px-4 lg:mx-0 lg:px-0">
        {/* Safety Guardian */}
        {latestReviews['SafetyGuardian'] && (
          <div className="flex-shrink-0 w-[280px] lg:w-auto">
            <AgentCard
              name="Safety Guardian"
              subtitle="Risk Assessment"
              score={latestReviews['SafetyGuardian'].safety_score ?? 0}
              summary={latestReviews['SafetyGuardian'].summary}
              rationale={latestReviews['SafetyGuardian'].rationale}
              colorScheme="green"
              icon={<SafetyIcon />}
            />
          </div>
        )}

        {/* Empathy Agent */}
        {latestReviews['EmpathyToneAgent'] && (
          <div className="flex-shrink-0 w-[280px] lg:w-auto">
            <AgentCard
              name="Empathy Agent"
              subtitle="Tone Analysis"
              score={latestReviews['EmpathyToneAgent'].empathy_score ?? 0}
              summary={latestReviews['EmpathyToneAgent'].summary}
              rationale={latestReviews['EmpathyToneAgent'].rationale}
              colorScheme="purple"
              icon={<EmpathyIcon />}
            />
          </div>
        )}

        {/* Clinical Critic */}
        {latestReviews['ClinicalCritic'] && (
          <div className="flex-shrink-0 w-[280px] lg:w-auto">
            <AgentCard
              name="Clinical Critic"
              subtitle="Evidence Review"
              score={latestReviews['ClinicalCritic'].clinical_score ?? 0}
              summary={latestReviews['ClinicalCritic'].summary}
              rationale={latestReviews['ClinicalCritic'].rationale}
              colorScheme="blue"
              icon={<ClinicalIcon />}
            />
          </div>
        )}

        {/* Empty State */}
        {Object.keys(latestReviews).length === 0 && (
          <EmptyState
            icon={<ChatEmptyIcon />}
            title="Waiting for agent evaluations..."
            description="Reviews will appear here as agents analyze the draft"
          />
        )}
      </div>

      {/* Drafting Notes */}
      {scratchpadNotes && (
        <div className="bg-white rounded-xl border border-gray-200 p-4 mt-4">
          <h3 className="font-semibold text-sm text-gray-800 mb-2 flex items-center gap-2">
            <EditIcon />
            Drafting Notes
          </h3>
          <p className="text-xs text-gray-600 leading-relaxed line-clamp-4">
            {scratchpadNotes}
          </p>
        </div>
      )}
    </div>
  </aside>
);
