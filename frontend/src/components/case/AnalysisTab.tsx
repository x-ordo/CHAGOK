'use client';

/**
 * AnalysisTab Component
 * Contains LSSP (Legal Strategy) and Precedent panels as sub-tabs.
 *
 * Lazy loads heavy panel components for better initial page load performance.
 *
 * Phase B.3: Added AI analysis status bar with last analyzed timestamp and request button.
 */

'use client';

/**
 * AnalysisTab Component
 * Contains LSSP (Legal Strategy) and Precedent panels as sub-tabs.
 *
 * Lazy loads heavy panel components for better initial page load performance.
 *
 * Phase B.3: Added AI analysis status bar with last analyzed timestamp and request button.
 */

import { Suspense, lazy } from 'react';
import { Sparkles, Clock, Loader2, RefreshCw } from 'lucide-react';

// Lazy load heavy panels for performance
const LSSPPanel = lazy(() =>
  import('@/components/lssp/LSSPPanel').then(mod => ({ default: mod.LSSPPanel }))
);

interface AnalysisTabProps {
  /** Case ID for data fetching */
  caseId: string;
  /** Number of evidence items in this case */
  evidenceCount: number;
  /** Callback when draft generation is requested */
  onDraftGenerate: (templateId?: string) => void;
  /** Last AI analysis timestamp (ISO 8601) */
  lastAnalyzedAt?: string;
  /** Handler for requesting AI analysis */
  onRequestAnalysis?: () => Promise<void>;
  /** Whether AI analysis is currently in progress */
  isAnalyzing?: boolean;
}

/**
 * Format relative time for last analysis timestamp
 */
function formatRelativeTime(isoDate: string): string {
  const now = new Date();
  const date = new Date(isoDate);
  const diffMs = now.getTime() - date.getTime();
  const diffMinutes = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMinutes < 1) return '방금 전';
  if (diffMinutes < 60) return `${diffMinutes}분 전`;
  if (diffHours < 24) return `${diffHours}시간 전`;
  if (diffDays < 7) return `${diffDays}일 전`;

  return date.toLocaleDateString('ko-KR', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * AI Analysis Status Bar Component
 */
function AIAnalysisStatusBar({
  lastAnalyzedAt,
  onRequestAnalysis,
  isAnalyzing,
}: {
  lastAnalyzedAt?: string;
  onRequestAnalysis?: () => Promise<void>;
  isAnalyzing?: boolean;
}) {
  const handleClick = async () => {
    if (onRequestAnalysis && !isAnalyzing) {
      await onRequestAnalysis();
    }
  };

  return (
    <div className="flex items-center justify-between p-4 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-xl border border-indigo-100 dark:border-indigo-800/50">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-indigo-100 dark:bg-indigo-900/50 rounded-lg">
          <Sparkles className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
        </div>
        <div>
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">
            AI 분석 상태
          </h4>
          <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {lastAnalyzedAt ? (
              <>마지막 분석: {formatRelativeTime(lastAnalyzedAt)}</>
            ) : (
              <>아직 분석되지 않음</>
            )}
          </p>
        </div>
      </div>
      <button
        type="button"
        onClick={handleClick}
        disabled={isAnalyzing}
        className={`inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
          isAnalyzing
            ? 'bg-gray-100 dark:bg-neutral-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'
            : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm'
        }`}
      >
        {isAnalyzing ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            분석 중...
          </>
        ) : (
          <>
            <RefreshCw className="w-4 h-4" />
            AI 분석 요청
          </>
        )}
      </button>
    </div>
  );
}

/**
 * Skeleton loader for lazy-loaded panels
 */
function PanelSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-6 bg-gray-200 dark:bg-neutral-700 rounded w-1/3" />
      <div className="h-4 bg-gray-200 dark:bg-neutral-700 rounded w-2/3" />
      <div className="space-y-3">
        <div className="h-24 bg-gray-200 dark:bg-neutral-700 rounded" />
        <div className="h-24 bg-gray-200 dark:bg-neutral-700 rounded" />
      </div>
    </div>
  );
}

/**
 * Analysis Tab - Contains LSSP (Legal Strategy) panel
 *
 * Features:
 * - Lazy loading of heavy panels for better initial load
 * - Sub-tab navigation flattened (Precedent integrated into LSSP)
 * - Skeleton loading states
 * - Draft generation callback integration
 * - AI analysis status bar with last analyzed timestamp (Phase B.3)
 */
export function AnalysisTab({
  caseId,
  evidenceCount,
  onDraftGenerate,
  lastAnalyzedAt,
  onRequestAnalysis,
  isAnalyzing = false,
}: AnalysisTabProps) {
  return (
    <div className="space-y-6">
      {/* AI Analysis Status Bar (Phase B.3) */}
      {onRequestAnalysis && (
        <AIAnalysisStatusBar
          lastAnalyzedAt={lastAnalyzedAt}
          onRequestAnalysis={onRequestAnalysis}
          isAnalyzing={isAnalyzing}
        />
      )}

      {/* Panel content with lazy loading */}
      <Suspense fallback={<PanelSkeleton />}>
        <LSSPPanel
          caseId={caseId}
          evidenceCount={evidenceCount}
          onDraftGenerate={onDraftGenerate}
        />
      </Suspense>
    </div>
  );
}
