'use client';

/**
 * AnalysisTab Component
 * Contains LSSP (Legal Strategy) and Precedent panels as sub-tabs.
 *
 * Lazy loads heavy panel components for better initial page load performance.
 */

import { useState, Suspense, lazy } from 'react';
import { Scale, FileText, LucideIcon } from 'lucide-react';

// Lazy load heavy panels for performance
const LSSPPanel = lazy(() =>
  import('@/components/lssp/LSSPPanel').then(mod => ({ default: mod.LSSPPanel }))
);
const PrecedentPanel = lazy(() =>
  import('@/components/precedent/PrecedentPanel').then(mod => ({ default: mod.PrecedentPanel }))
);

interface AnalysisTabProps {
  /** Case ID for data fetching */
  caseId: string;
  /** Number of evidence items in this case */
  evidenceCount: number;
  /** Callback when draft generation is requested */
  onDraftGenerate: (templateId?: string) => void;
}

type SectionId = 'lssp' | 'precedent';

interface SubTabConfig {
  id: SectionId;
  label: string;
  icon: LucideIcon;
}

const SUB_TABS: SubTabConfig[] = [
  { id: 'lssp', label: '법률 전략 (LSSP)', icon: FileText },
  { id: 'precedent', label: '유사 판례', icon: Scale },
];

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
 * Sub-tab button component
 */
function SubTabButton({
  tab,
  isActive,
  onClick,
}: {
  tab: SubTabConfig;
  isActive: boolean;
  onClick: () => void;
}) {
  const Icon = tab.icon;

  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex items-center gap-2 pb-3 text-sm font-medium border-b-2 transition-colors ${
        isActive
          ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
          : 'border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
      }`}
    >
      <Icon className="w-4 h-4" />
      {tab.label}
    </button>
  );
}

/**
 * Analysis Tab - Contains LSSP and Precedent sub-tabs
 *
 * Features:
 * - Lazy loading of heavy panels for better initial load
 * - Sub-tab navigation between LSSP and Precedent
 * - Skeleton loading states
 * - Draft generation callback integration
 */
export function AnalysisTab({ caseId, evidenceCount, onDraftGenerate }: AnalysisTabProps) {
  const [activeSection, setActiveSection] = useState<SectionId>('lssp');

  return (
    <div className="space-y-6">
      {/* Sub-tab navigation */}
      <div className="flex gap-6 border-b border-gray-200 dark:border-neutral-700">
        {SUB_TABS.map((tab) => (
          <SubTabButton
            key={tab.id}
            tab={tab}
            isActive={activeSection === tab.id}
            onClick={() => setActiveSection(tab.id)}
          />
        ))}
      </div>

      {/* Panel content with lazy loading */}
      <Suspense fallback={<PanelSkeleton />}>
        {activeSection === 'lssp' && (
          <LSSPPanel
            caseId={caseId}
            evidenceCount={evidenceCount}
            onDraftGenerate={onDraftGenerate}
          />
        )}
        {activeSection === 'precedent' && (
          <PrecedentPanel caseId={caseId} />
        )}
      </Suspense>
    </div>
  );
}
