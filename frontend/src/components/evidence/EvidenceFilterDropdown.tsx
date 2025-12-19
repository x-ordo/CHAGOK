'use client';

/**
 * EvidenceFilterDropdown Component
 * Extracted from LawyerCaseDetailClient for reusability.
 *
 * Provides filtering by file type and processing status.
 */

import { Filter } from 'lucide-react';
import { EvidenceType, EvidenceStatus } from '@/types/evidence';

interface EvidenceFilterDropdownProps {
  /** Current filter by file type */
  filterType: EvidenceType | 'all';
  /** Current filter by processing status */
  filterStatus: EvidenceStatus | 'all';
  /** Handler for type filter change */
  onFilterTypeChange: (type: EvidenceType | 'all') => void;
  /** Handler for status filter change */
  onFilterStatusChange: (status: EvidenceStatus | 'all') => void;
  /** Reset all filters to default */
  onReset: () => void;
  /** Whether the dropdown is open */
  isOpen: boolean;
  /** Toggle dropdown open/close */
  onToggle: () => void;
}

const FILE_TYPES: { value: EvidenceType | 'all'; label: string }[] = [
  { value: 'all', label: '전체' },
  { value: 'text', label: '텍스트' },
  { value: 'image', label: '이미지' },
  { value: 'audio', label: '오디오' },
  { value: 'video', label: '비디오' },
  { value: 'pdf', label: 'PDF' },
];

const STATUS_OPTIONS: { value: EvidenceStatus | 'all'; label: string }[] = [
  { value: 'all', label: '전체' },
  { value: 'queued', label: '대기중' },
  { value: 'processing', label: '처리중' },
  { value: 'completed', label: '완료' },
  { value: 'failed', label: '실패' },
];

/**
 * Dropdown component for filtering evidence by type and status
 */
export function EvidenceFilterDropdown({
  filterType,
  filterStatus,
  onFilterTypeChange,
  onFilterStatusChange,
  onReset,
  isOpen,
  onToggle,
}: EvidenceFilterDropdownProps) {
  const hasActiveFilters = filterType !== 'all' || filterStatus !== 'all';

  return (
    <div className="relative">
      {/* Trigger Button */}
      <button
        type="button"
        onClick={onToggle}
        className={`flex items-center text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] bg-white dark:bg-neutral-800 border px-3 py-1.5 rounded-md shadow-sm transition-colors ${
          hasActiveFilters
            ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
            : 'border-gray-300 dark:border-neutral-600'
        }`}
      >
        <Filter className="w-4 h-4 mr-2" />
        필터{hasActiveFilters && ' (활성)'}
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-neutral-800 border border-gray-300 dark:border-neutral-600 rounded-lg shadow-lg z-20 p-4">
          {/* Type Filter */}
          <div className="mb-3">
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              파일 타입
            </label>
            <select
              value={filterType}
              onChange={(e) => onFilterTypeChange(e.target.value as EvidenceType | 'all')}
              className="w-full text-sm border border-gray-300 dark:border-neutral-600 rounded-md px-2 py-1.5 bg-white dark:bg-neutral-700 text-[var(--color-text-primary)]"
            >
              {FILE_TYPES.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div className="mb-3">
            <label className="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
              처리 상태
            </label>
            <select
              value={filterStatus}
              onChange={(e) => onFilterStatusChange(e.target.value as EvidenceStatus | 'all')}
              className="w-full text-sm border border-gray-300 dark:border-neutral-600 rounded-md px-2 py-1.5 bg-white dark:bg-neutral-700 text-[var(--color-text-primary)]"
            >
              {STATUS_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Footer */}
          <div className="flex justify-between items-center pt-2 border-t border-gray-200 dark:border-neutral-700">
            <button
              type="button"
              onClick={onReset}
              className="text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
            >
              필터 초기화
            </button>
            <button
              type="button"
              onClick={onToggle}
              className="text-xs text-[var(--color-primary)] hover:underline"
            >
              닫기
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
