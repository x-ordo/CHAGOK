/**
 * Hook for Case ID Validation with Timeout Prevention
 *
 * Replaces the duplicated setTimeout hack pattern found in:
 * - LawyerCaseDetailClient.tsx (lines 134-189)
 * - CaseDetailClient.tsx (similar pattern)
 *
 * This hook:
 * 1. Uses useCaseIdFromUrl to extract case ID from URL
 * 2. Manages timeout state to prevent infinite spinners
 * 3. Provides validation flags for conditional rendering
 *
 * @example
 * ```tsx
 * function CaseDetailPage({ id }: { id: string }) {
 *   const { caseId, isIdMissing, idWaitTimedOut } = useCaseIdValidation(id);
 *
 *   if (isIdMissing && idWaitTimedOut) {
 *     return <ErrorState message="사건 ID를 찾을 수 없습니다." />;
 *   }
 *
 *   if (isIdMissing) {
 *     return <LoadingSpinner />; // Wait for URL params
 *   }
 *
 *   // caseId is valid, proceed with data fetching
 * }
 * ```
 */

'use client';

import { useState, useEffect, useMemo } from 'react';
import { useCaseIdFromUrl } from './useCaseIdFromUrl';

export interface UseCaseIdValidationOptions {
  /**
   * Timeout duration in milliseconds before showing error state
   * @default 2000
   */
  timeoutMs?: number;
}

export interface UseCaseIdValidationReturn {
  /**
   * The validated case ID (empty string if missing)
   */
  caseId: string;

  /**
   * Whether the case ID is missing or empty
   */
  isIdMissing: boolean;

  /**
   * Whether the timeout has elapsed while waiting for ID
   * Used to prevent infinite spinners
   */
  idWaitTimedOut: boolean;

  /**
   * Whether the case ID is valid (not missing and not timed out)
   */
  isValid: boolean;
}

const DEFAULT_TIMEOUT_MS = 2000;

export function useCaseIdValidation(
  paramId: string,
  options?: UseCaseIdValidationOptions
): UseCaseIdValidationReturn {
  const { timeoutMs = DEFAULT_TIMEOUT_MS } = options || {};

  // Extract case ID from URL (query param > path segment > fallback)
  const id = useCaseIdFromUrl(paramId);
  const caseId = id || '';

  // Memoize the missing check to prevent unnecessary recalculations
  const isIdMissing = useMemo(() => !id || id.trim() === '', [id]);

  // Timeout state for infinite spinner prevention
  const [idWaitTimedOut, setIdWaitTimedOut] = useState(false);

  // Set timeout to prevent infinite waiting
  useEffect(() => {
    // Reset timeout state when ID becomes available
    if (!isIdMissing) {
      setIdWaitTimedOut(false);
      return;
    }

    // Set timeout to show error state
    const timeout = setTimeout(() => {
      if (isIdMissing) {
        setIdWaitTimedOut(true);
      }
    }, timeoutMs);

    return () => clearTimeout(timeout);
  }, [isIdMissing, timeoutMs]);

  // Convenience flag: ID is valid for use
  const isValid = !isIdMissing && !idWaitTimedOut;

  return {
    caseId,
    isIdMissing,
    idWaitTimedOut,
    isValid,
  };
}

export default useCaseIdValidation;
