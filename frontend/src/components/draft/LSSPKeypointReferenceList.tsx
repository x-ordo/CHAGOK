/**
 * LSSPKeypointReferenceList Component
 *
 * Displays LSSP keypoints in a compact card format for reference while drafting.
 * Allows users to insert keypoint citations into the draft editor.
 *
 * Part of Phase B.2 (DraftSplitView) implementation.
 */

'use client';

import React from 'react';
import {
  Tag,
  Quote,
  CheckCircle2,
  Circle,
  AlertTriangle,
  Sparkles,
  User,
  Link2,
} from 'lucide-react';
import { Keypoint, LegalGround } from '@/lib/api/lssp';

// =============================================================================
// Types
// =============================================================================

export interface LSSPKeypointReferenceListProps {
  /**
   * List of keypoints to display
   */
  keypoints: Keypoint[];

  /**
   * Handler when user clicks to insert a keypoint citation
   * @param keypointId - The keypoint ID to cite
   * @param content - The keypoint content text
   */
  onInsertCitation: (keypointId: string, content: string) => void;

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

const getSourceIcon = (sourceType: Keypoint['source_type']) => {
  switch (sourceType) {
    case 'ai_extracted':
      return <Sparkles className="w-3 h-3 text-indigo-500" />;
    case 'user_added':
      return <User className="w-3 h-3 text-blue-500" />;
    case 'merged':
      return <Link2 className="w-3 h-3 text-purple-500" />;
  }
};

const getSourceLabel = (sourceType: Keypoint['source_type']): string => {
  switch (sourceType) {
    case 'ai_extracted':
      return 'AI 추출';
    case 'user_added':
      return '직접 추가';
    case 'merged':
      return '병합됨';
  }
};

const getConfidenceColor = (score: number | null): string => {
  if (score === null) return 'bg-gray-100 text-gray-600 dark:bg-neutral-700 dark:text-gray-400';
  if (score >= 0.8) return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300';
  if (score >= 0.5) return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300';
  return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300';
};

// =============================================================================
// Component
// =============================================================================

export function LSSPKeypointReferenceList({
  keypoints,
  onInsertCitation,
  isLoading = false,
  className = '',
}: LSSPKeypointReferenceListProps) {
  if (isLoading) {
    return (
      <div className={`p-4 ${className}`}>
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-24 bg-gray-200 dark:bg-neutral-700 rounded-lg"
            />
          ))}
        </div>
      </div>
    );
  }

  if (keypoints.length === 0) {
    return (
      <div className={`p-4 text-center ${className}`}>
        <Tag className="w-8 h-8 mx-auto text-gray-400 mb-2" />
        <p className="text-sm text-gray-500 dark:text-gray-400">
          핵심 쟁점이 없습니다.
        </p>
        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
          분석 탭에서 AI 쟁점 추출을 실행해보세요.
        </p>
      </div>
    );
  }

  return (
    <div className={`space-y-2 p-2 ${className}`}>
      {keypoints.map((keypoint) => {
        const linkedGrounds = keypoint.legal_grounds || [];

        return (
          <div
            key={keypoint.id}
            className={`p-3 border rounded-lg transition-colors ${
              keypoint.user_verified
                ? 'bg-green-50/50 dark:bg-green-900/10 border-green-200 dark:border-green-800'
                : 'bg-white dark:bg-neutral-800 border-gray-200 dark:border-neutral-700 hover:border-indigo-300 dark:hover:border-indigo-600'
            }`}
          >
            {/* Header Row */}
            <div className="flex items-start gap-2 mb-2">
              <div className="mt-0.5 flex-shrink-0">
                {keypoint.user_verified ? (
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                ) : (
                  <Circle className="w-4 h-4 text-gray-300 dark:text-gray-600" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-900 dark:text-gray-100 line-clamp-3">
                  {keypoint.content}
                </p>
              </div>
            </div>

            {/* Meta info */}
            <div className="flex flex-wrap items-center gap-1.5 mb-2">
              {/* Source type */}
              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs bg-gray-100 dark:bg-neutral-700 text-gray-600 dark:text-gray-400">
                {getSourceIcon(keypoint.source_type)}
                <span>{getSourceLabel(keypoint.source_type)}</span>
              </span>

              {/* Confidence score */}
              {keypoint.confidence_score !== null && (
                <span
                  className={`px-1.5 py-0.5 rounded text-xs ${getConfidenceColor(
                    keypoint.confidence_score
                  )}`}
                >
                  {Math.round(keypoint.confidence_score * 100)}%
                </span>
              )}

              {/* Disputed flag */}
              {keypoint.is_disputed && (
                <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300">
                  <AlertTriangle className="w-3 h-3" />
                  쟁점
                </span>
              )}
            </div>

            {/* Legal grounds */}
            {linkedGrounds.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-2">
                {linkedGrounds.slice(0, 2).map((ground) => (
                  <span
                    key={ground.code}
                    className="px-1.5 py-0.5 text-xs bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded"
                  >
                    {ground.code}
                  </span>
                ))}
                {linkedGrounds.length > 2 && (
                  <span className="text-xs text-gray-400">
                    +{linkedGrounds.length - 2}
                  </span>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="pt-2 border-t border-gray-100 dark:border-neutral-700">
              <button
                type="button"
                onClick={() => onInsertCitation(keypoint.id, keypoint.content)}
                className="w-full flex items-center justify-center gap-1.5 px-2 py-1.5 text-xs font-medium text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 rounded transition-colors"
              >
                <Quote className="w-3.5 h-3.5" />
                쟁점 인용
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default LSSPKeypointReferenceList;
