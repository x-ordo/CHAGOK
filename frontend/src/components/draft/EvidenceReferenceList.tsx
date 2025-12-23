/**
 * EvidenceReferenceList Component
 *
 * Displays a list of evidence items in a compact card format for reference while drafting.
 * Allows users to insert citations from evidence into the draft editor.
 *
 * Part of Phase B.2 (DraftSplitView) implementation.
 */

'use client';

import React from 'react';
import {
  FileText,
  Image,
  Video,
  Mic,
  File,
  Quote,
  ExternalLink,
  Tag,
} from 'lucide-react';
import { Evidence, EvidenceType } from '@/types/evidence';
import { getEvidenceStatusConfig } from '@/lib/utils/statusConfig';

// =============================================================================
// Types
// =============================================================================

export interface EvidenceReferenceListProps {
  /**
   * List of evidence items to display
   */
  items: Evidence[];

  /**
   * Handler when user clicks to insert a citation
   * @param evidenceId - The evidence ID to cite
   * @param quote - Optional quote/excerpt text to include
   */
  onInsertCitation: (evidenceId: string, quote?: string) => void;

  /**
   * Handler to view evidence details (optional)
   * @param evidenceId - The evidence ID to view
   */
  onViewEvidence?: (evidenceId: string) => void;

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

const getTypeIcon = (type: EvidenceType) => {
  switch (type) {
    case 'image':
      return <Image className="w-4 h-4" />;
    case 'video':
      return <Video className="w-4 h-4" />;
    case 'audio':
      return <Mic className="w-4 h-4" />;
    case 'text':
    case 'pdf':
      return <FileText className="w-4 h-4" />;
    default:
      return <File className="w-4 h-4" />;
  }
};

const getTypeLabel = (type: EvidenceType): string => {
  switch (type) {
    case 'image':
      return '이미지';
    case 'video':
      return '영상';
    case 'audio':
      return '음성';
    case 'text':
      return '텍스트';
    case 'pdf':
      return 'PDF';
    default:
      return '파일';
  }
};

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('ko-KR', {
    month: 'short',
    day: 'numeric',
  });
};

// =============================================================================
// Component
// =============================================================================

export function EvidenceReferenceList({
  items,
  onInsertCitation,
  onViewEvidence,
  isLoading = false,
  className = '',
}: EvidenceReferenceListProps) {
  if (isLoading) {
    return (
      <div className={`p-4 ${className}`}>
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-20 bg-gray-200 dark:bg-neutral-700 rounded-lg"
            />
          ))}
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className={`p-4 text-center ${className}`}>
        <FileText className="w-8 h-8 mx-auto text-gray-400 mb-2" />
        <p className="text-sm text-gray-500 dark:text-gray-400">
          증거 자료가 없습니다.
        </p>
      </div>
    );
  }

  return (
    <div className={`space-y-2 p-2 ${className}`}>
      {items.map((evidence) => {
        const statusConfig = getEvidenceStatusConfig(evidence.status);

        return (
          <div
            key={evidence.id}
            className="p-3 bg-white dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 transition-colors"
          >
            {/* Header Row */}
            <div className="flex items-start gap-2 mb-2">
              <div className="p-1.5 bg-gray-100 dark:bg-neutral-700 rounded">
                {getTypeIcon(evidence.type)}
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                  {evidence.filename}
                </h4>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {getTypeLabel(evidence.type)}
                  </span>
                  <span className="text-xs text-gray-400 dark:text-gray-500">
                    {formatDate(evidence.uploadDate)}
                  </span>
                </div>
              </div>
              <span
                className={`px-1.5 py-0.5 text-xs font-medium rounded ${statusConfig.color}`}
              >
                {statusConfig.label}
              </span>
            </div>

            {/* Summary (if available) */}
            {evidence.summary && (
              <p className="text-xs text-gray-600 dark:text-gray-400 mb-2 line-clamp-2">
                {evidence.summary}
              </p>
            )}

            {/* Labels (if available) */}
            {evidence.labels && evidence.labels.length > 0 && (
              <div className="flex items-center gap-1 mb-2 flex-wrap">
                <Tag className="w-3 h-3 text-gray-400" />
                {evidence.labels.slice(0, 3).map((label, idx) => (
                  <span
                    key={idx}
                    className="px-1.5 py-0.5 text-xs bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded"
                  >
                    {label}
                  </span>
                ))}
                {evidence.labels.length > 3 && (
                  <span className="text-xs text-gray-400">
                    +{evidence.labels.length - 3}
                  </span>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center gap-2 mt-2 pt-2 border-t border-gray-100 dark:border-neutral-700">
              <button
                type="button"
                onClick={() => onInsertCitation(evidence.id)}
                className="flex-1 flex items-center justify-center gap-1.5 px-2 py-1.5 text-xs font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/50 rounded transition-colors"
              >
                <Quote className="w-3.5 h-3.5" />
                인용 삽입
              </button>
              {onViewEvidence && (
                <button
                  type="button"
                  onClick={() => onViewEvidence(evidence.id)}
                  className="p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-neutral-700 rounded transition-colors"
                  title="상세 보기"
                >
                  <ExternalLink className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default EvidenceReferenceList;
