'use client';

/**
 * useCaseDetail Hook
 * Encapsulates case detail fetching, loading state, error handling, and mapping.
 *
 * Following CTO feedback: Complete separation of data fetching from UI rendering.
 */

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api/client';
import { CaseDetailApiResponse } from '@/lib/api/caseDetail';
import { CaseDetail } from '@/types/caseDetail';
import { mapApiCaseDetailToCaseDetail } from '@/lib/utils/caseDetailMapper';

interface UseCaseDetailReturn {
  /** Case detail data (null while loading or on error) */
  data: CaseDetail | null;
  /** Whether the data is currently being fetched */
  isLoading: boolean;
  /** Error message if fetch failed */
  error: string | null;
  /** Refetch case detail data */
  refetch: () => Promise<void>;
}

/**
 * Hook to fetch and manage case detail data
 *
 * @param caseId - The case ID to fetch details for (can be null during URL parsing)
 * @returns Object with data, loading state, error, and refetch function
 *
 * @example
 * ```tsx
 * const { data: caseDetail, isLoading, error, refetch } = useCaseDetail(caseId);
 *
 * if (isLoading) return <PageSkeleton />;
 * if (error) return <ErrorState message={error} onRetry={refetch} />;
 * if (!caseDetail) return null;
 *
 * return <CaseDetailView caseDetail={caseDetail} />;
 * ```
 */
export function useCaseDetail(caseId: string | null): UseCaseDetailReturn {
  const router = useRouter();
  const [data, setData] = useState<CaseDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCaseDetail = useCallback(async () => {
    if (!caseId) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<CaseDetailApiResponse>(`/lawyer/cases/${caseId}`);

      if (response.error || !response.data) {
        // Handle authentication errors
        if (response.status === 401) {
          router.push('/login');
          return;
        }

        throw new Error(response.error || '케이스 정보를 불러오는데 실패했습니다.');
      }

      setData(mapApiCaseDetailToCaseDetail(response.data));
    } catch (err) {
      setError(err instanceof Error ? err.message : '오류가 발생했습니다.');
      setData(null);
    } finally {
      setIsLoading(false);
    }
  }, [caseId, router]);

  useEffect(() => {
    let isCancelled = false;

    const fetchData = async () => {
      if (isCancelled) return;
      await fetchCaseDetail();
    };

    fetchData();

    // Cleanup: prevent state updates after unmount or caseId change
    return () => {
      isCancelled = true;
    };
  }, [fetchCaseDetail]);

  return {
    data,
    isLoading,
    error,
    refetch: fetchCaseDetail,
  };
}
