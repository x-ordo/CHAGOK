/**
 * PrecedentReferenceList Component
 *
 * Displays similar precedents in a compact card format for reference while drafting.
 * Allows users to insert precedent citations into the draft editor.
 *
 * Part of Phase B.2 (DraftSplitView) implementation.
 */

'use client';

import React from 'react';
import {
  Scale,
  Quote,
  ExternalLink,
  Calendar,
  Building2,
} from 'lucide-react';
import { PrecedentCitation } from '@/types/draft';

// =============================================================================
// Types
// =============================================================================

export interface PrecedentReferenceListProps {
  /**
   * List of precedent citations to display
   */
  precedents: PrecedentCitation[];

  /**
   * Handler when user clicks to insert a precedent citation
   * @param caseRef - The case reference (사건번호)
   * @param summary - The precedent summary
   */
  onInsertCitation: (caseRef: string, summary: string) => void;

  /**
   * Whether the list is loading
   */
  isLoading?: boolean;

  /**
   * Additional CSS classes
   */
  className?: string;
}

// =============================================================================
// Helpers
// =============================================================================

const getSimilarityColor = (score: number): string => {
  if (score >= 0.8) return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/30';
  if (score >= 0.6) return 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30';
  if (score >= 0.4) return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/30';
  return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-neutral-700';
};

const formatDate = (dateString: string): string => {
  try {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateString;
  }
};

// =============================================================================
// Component
// =============================================================================

export function PrecedentReferenceList({
  precedents,
  onInsertCitation,
  isLoading = false,
  className = '',
}: PrecedentReferenceListProps) {
  if (isLoading) {
    return (
      <div className={`p-4 ${className}`}>
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-28 bg-gray-200 dark:bg-neutral-700 rounded-lg"
            />
          ))}
        </div>
      </div>
    );
  }

  if (precedents.length === 0) {
    return (
      <div className={`p-4 text-center ${className}`}>
        <Scale className="w-8 h-8 mx-auto text-gray-400 mb-2" />
        <p className="text-sm text-gray-500 dark:text-gray-400">
          유사 판례가 없습니다.
        </p>
        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
          초안 생성 시 관련 판례가 자동으로 검색됩니다.
        </p>
      </div>
    );
  }

  return (
    <div className={`space-y-2 p-2 ${className}`}>
      {precedents.map((precedent, index) => (
        <div
          key={`${precedent.case_ref}-${index}`}
          className="p-3 bg-white dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 transition-colors"
        >
          {/* Header Row */}
          <div className="flex items-start justify-between gap-2 mb-2">
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {precedent.case_ref}
              </h4>
              <div className="flex items-center gap-2 mt-0.5 text-xs text-gray-500 dark:text-gray-400">
                <span className="inline-flex items-center gap-1">
                  <Building2 className="w-3 h-3" />
                  {precedent.court}
                </span>
                <span className="inline-flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {formatDate(precedent.decision_date)}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-1.5">
              <span
                className={`px-2 py-0.5 text-xs font-medium rounded ${getSimilarityColor(
                  precedent.similarity_score
                )}`}
              >
                {Math.round(precedent.similarity_score * 100)}%
              </span>
              {precedent.source_url && (
                <a
                  href={precedent.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1 text-gray-400 hover:text-blue-500 dark:hover:text-blue-400 transition-colors"
                  title="법령정보센터에서 원문 보기"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>
          </div>

          {/* Summary */}
          <p className="text-xs text-gray-600 dark:text-gray-400 mb-2 line-clamp-3">
            {precedent.summary}
          </p>

          {/* Key factors */}
          {precedent.key_factors && precedent.key_factors.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {precedent.key_factors.slice(0, 3).map((factor, idx) => (
                <span
                  key={idx}
                  className="px-1.5 py-0.5 text-xs bg-gray-100 dark:bg-neutral-700 text-gray-600 dark:text-gray-400 rounded"
                >
                  {factor}
                </span>
              ))}
              {precedent.key_factors.length > 3 && (
                <span className="text-xs text-gray-400">
                  +{precedent.key_factors.length - 3}
                </span>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="pt-2 border-t border-gray-100 dark:border-neutral-700">
            <button
              type="button"
              onClick={() =>
                onInsertCitation(precedent.case_ref, precedent.summary)
              }
              className="w-full flex items-center justify-center gap-1.5 px-2 py-1.5 text-xs font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/50 rounded transition-colors"
            >
              <Quote className="w-3.5 h-3.5" />
              판례 인용
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

export default PrecedentReferenceList;
