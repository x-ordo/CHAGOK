'use client';

/**
 * useDraft Hook
 * Encapsulates draft generation, preview, and download functionality.
 *
 * Extracted from LawyerCaseDetailClient to separate concerns.
 */

import { useState, useCallback } from 'react';
import { generateDraftPreview } from '@/lib/api/draft';
import { downloadDraftAsDocx, DraftDownloadFormat, DownloadResult } from '@/services/documentService';
import { DraftCitation } from '@/types/draft';
import { logger } from '@/lib/logger';

interface UseDraftReturn {
  // Modal state
  /** Whether the draft generation modal is open */
  showDraftModal: boolean;
  /** Open the draft generation modal */
  openDraftModal: () => void;
  /** Close the draft generation modal */
  closeDraftModal: () => void;

  // Draft content
  /** The generated draft text */
  draftText: string;
  /** Citations used in the draft */
  draftCitations: DraftCitation[];
  /** Whether there is an existing draft to display */
  hasExistingDraft: boolean;

  // Loading/error states
  /** Whether draft generation is in progress */
  isGenerating: boolean;
  /** Error message if generation failed */
  error: string | null;

  // Actions
  /** Generate a new draft */
  generateDraft: (selectedEvidenceIds?: string[]) => Promise<void>;
  /** Download the draft in specified format */
  downloadDraft: (data: { format: DraftDownloadFormat; content: string }) => Promise<DownloadResult>;
  /** Open modal to regenerate draft */
  regenerateDraft: () => void;
  /** Clear the current draft */
  clearDraft: () => void;
}

/**
 * Hook to manage draft generation and preview state
 *
 * @param caseId - The case ID to generate drafts for
 * @returns Object with draft state and actions
 *
 * @example
 * ```tsx
 * const draft = useDraft(caseId);
 *
 * // In modal trigger
 * <button onClick={draft.openDraftModal}>Generate Draft</button>
 *
 * // In draft panel
 * <DraftPreviewPanel
 *   draftText={draft.draftText}
 *   citations={draft.draftCitations}
 *   isGenerating={draft.isGenerating}
 *   hasExistingDraft={draft.hasExistingDraft}
 *   onGenerate={draft.regenerateDraft}
 *   onDownload={draft.downloadDraft}
 * />
 * ```
 */
export function useDraft(caseId: string | null): UseDraftReturn {
  // Modal state
  const [showDraftModal, setShowDraftModal] = useState(false);

  // Draft content
  const [draftText, setDraftText] = useState('');
  const [draftCitations, setDraftCitations] = useState<DraftCitation[]>([]);
  const [hasExistingDraft, setHasExistingDraft] = useState(false);

  // Loading/error states
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Modal actions
  const openDraftModal = useCallback(() => setShowDraftModal(true), []);
  const closeDraftModal = useCallback(() => setShowDraftModal(false), []);

  // Clear draft
  const clearDraft = useCallback(() => {
    setDraftText('');
    setDraftCitations([]);
    setHasExistingDraft(false);
    setError(null);
  }, []);

  // Generate draft
  const generateDraft = useCallback(async (selectedEvidenceIds?: string[]) => {
    if (!caseId) return;

    setIsGenerating(true);
    setError(null);

    try {
      const response = await generateDraftPreview(caseId, {
        sections: ['청구취지', '청구원인'],
        language: 'ko',
        style: '법원 제출용_표준',
      });

      if (response.error || !response.data) {
        throw new Error(response.error || '초안 생성에 실패했습니다.');
      }

      const { draft_text, citations } = response.data;

      // Map API citations to component format
      const mappedCitations: DraftCitation[] = citations.map(c => ({
        evidenceId: c.evidence_id,
        title: c.snippet.substring(0, 50) + (c.snippet.length > 50 ? '...' : ''),
        quote: c.snippet,
      }));

      setDraftText(draft_text);
      setDraftCitations(mappedCitations);
      setHasExistingDraft(true);
      setShowDraftModal(false);
    } catch (err) {
      logger.error('Draft generation error:', err);
      setError(err instanceof Error ? err.message : '초안 생성에 실패했습니다.');
    } finally {
      setIsGenerating(false);
    }
  }, [caseId]);

  // Download draft
  const downloadDraft = useCallback(async (data: { format: DraftDownloadFormat; content: string }): Promise<DownloadResult> => {
    if (!caseId) {
      return {
        success: false,
        error: 'Case ID is required for download',
      };
    }

    try {
      const result = await downloadDraftAsDocx(data.content, caseId, data.format);
      return result;
    } catch (err) {
      logger.error('Draft download error:', err);
      return {
        success: false,
        error: err instanceof Error ? err.message : '다운로드에 실패했습니다.',
      };
    }
  }, [caseId]);

  // Regenerate (opens modal)
  const regenerateDraft = useCallback(() => {
    setShowDraftModal(true);
  }, []);

  return {
    showDraftModal,
    openDraftModal,
    closeDraftModal,
    draftText,
    draftCitations,
    hasExistingDraft,
    isGenerating,
    error,
    generateDraft,
    downloadDraft,
    regenerateDraft,
    clearDraft,
  };
}
