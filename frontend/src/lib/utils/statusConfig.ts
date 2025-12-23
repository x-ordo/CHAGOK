/**
 * Unified Status Configuration
 *
 * Centralizes all status-related colors and labels across the application.
 * Replaces duplicated status configurations in:
 * - LawyerCaseDetailClient.tsx
 * - ClientCaseDetailClient.tsx
 * - DetectiveCaseDetailClient.tsx
 * - CaseCard.tsx
 * - CaseTable.tsx
 * - staff/progress/page.tsx
 */

// =============================================================================
// Case Status Configuration
// =============================================================================

export const CASE_STATUS_COLORS: Record<string, string> = {
  // Lawyer/Staff statuses
  active: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  open: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  in_progress: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
  closed: 'bg-gray-100 text-gray-800 dark:bg-neutral-700 dark:text-neutral-300',

  // Detective statuses
  pending: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
  review: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300',
  completed: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',

  // Staff progress statuses
  blocked: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
  waiting: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
};

export const CASE_STATUS_LABELS: Record<string, string> = {
  // Lawyer/Staff statuses
  active: '활성',
  open: '진행 중',
  in_progress: '검토 대기',
  closed: '종료',

  // Detective statuses
  pending: '대기중',
  review: '검토중',
  completed: '완료',

  // Staff progress statuses
  blocked: '차단됨',
  waiting: '대기',
};

// =============================================================================
// Evidence Status Configuration
// =============================================================================

export const EVIDENCE_STATUS_COLORS: Record<string, string> = {
  verified: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
  approved: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
  processed: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
  pending_review: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
  rejected: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
  processing: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300',
  queued: 'bg-gray-100 text-gray-600 dark:bg-neutral-700 dark:text-neutral-400',
  uploading: 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400',
  failed: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
};

export const EVIDENCE_STATUS_LABELS: Record<string, string> = {
  verified: '검증완료',
  approved: '승인됨',
  processed: '분석완료',
  pending_review: '검토 대기',
  rejected: '반려됨',
  processing: '처리중',
  queued: '대기열',
  uploading: '업로드 중',
  failed: '실패',
};

// =============================================================================
// Helper Functions
// =============================================================================

export interface StatusConfig {
  color: string;
  label: string;
}

/**
 * Get case status configuration (color and label)
 */
export function getCaseStatusConfig(status: string): StatusConfig {
  return {
    color: CASE_STATUS_COLORS[status] || CASE_STATUS_COLORS.active,
    label: CASE_STATUS_LABELS[status] || status,
  };
}

/**
 * Get evidence status configuration (color and label)
 */
export function getEvidenceStatusConfig(status: string): StatusConfig {
  return {
    color: EVIDENCE_STATUS_COLORS[status] || 'bg-gray-100 text-gray-600 dark:bg-neutral-700 dark:text-neutral-400',
    label: EVIDENCE_STATUS_LABELS[status] || '처리중',
  };
}

/**
 * Get case status badge CSS classes
 */
export function getCaseStatusBadgeClasses(status: string): string {
  return CASE_STATUS_COLORS[status] || CASE_STATUS_COLORS.active;
}

/**
 * Get evidence status badge CSS classes
 */
export function getEvidenceStatusBadgeClasses(status: string): string {
  return EVIDENCE_STATUS_COLORS[status] || 'bg-gray-100 text-gray-600 dark:bg-neutral-700 dark:text-neutral-400';
}

/**
 * Get case status label
 */
export function getCaseStatusLabel(status: string): string {
  return CASE_STATUS_LABELS[status] || status;
}

/**
 * Get evidence status label
 */
export function getEvidenceStatusLabel(status: string): string {
  return EVIDENCE_STATUS_LABELS[status] || '처리중';
}
