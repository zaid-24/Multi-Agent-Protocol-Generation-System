/**
 * Cerina Protocol Foundry - UI Component Library
 * 
 * Centralized exports for all reusable UI components.
 * Import from '@/components/ui' for consistent styling.
 */

// ========== BUTTONS ==========
export { 
  Button, 
  PrimaryButton, 
  SecondaryButton, 
  SuccessButton, 
  DangerButton 
} from '../Button';

// ========== STATUS & BADGES ==========
export { StatusBadge } from '../StatusBadge';

// ========== CARDS ==========
export { Card, CardHeader } from '../Card';
export { AgentCard } from '../AgentCard';

// ========== LOADING & SKELETON ==========
export { Spinner, LoadingState } from '../Spinner';
export { 
  Skeleton, 
  SkeletonCard, 
  SkeletonText, 
  SessionDetailSkeleton 
} from '../Skeleton';

// ========== METRICS & SCORES ==========
export { MetricItem, MetricGroup } from './MetricItem';
export { ScoreBar, ScoreGroup } from './ScoreBar';
export { ProgressBar } from './ProgressBar';

// ========== HEADERS & LAYOUT ==========
export { SectionHeader, PageHeader } from './SectionHeader';
export { EmptyState, DocumentEmptyIcon, ChatEmptyIcon } from './EmptyState';

// ========== ICONS ==========
export {
  // Navigation
  BackIcon,
  ChevronRightIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  // Actions
  PlusIcon,
  LightningIcon,
  EditIcon,
  // Status
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  // Documents
  DocumentIcon,
  // Agent Icons
  SafetyIcon,
  EmpathyIcon,
  ClinicalIcon,
  // Loading
  SpinnerIcon,
} from './Icons';
