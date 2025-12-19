/**
 * Hook for Evidence Upload with Progress Tracking
 *
 * Extracts ~100 lines of duplicated upload logic from:
 * - LawyerCaseDetailClient.tsx (lines 324-421)
 * - CaseDetailClient.tsx (lines 230-331)
 *
 * This hook handles:
 * 1. Presigned URL acquisition from backend
 * 2. Direct S3 upload with progress tracking
 * 3. Upload completion notification
 * 4. Feedback message management
 *
 * @example
 * ```tsx
 * function EvidenceSection({ caseId }: { caseId: string }) {
 *   const { handleUpload, uploadStatus, uploadFeedback, isUploading } = useEvidenceUpload(caseId, {
 *     onUploadComplete: () => refetchEvidence(),
 *   });
 *
 *   return (
 *     <EvidenceUploadZone onUpload={handleUpload}>
 *       {isUploading && <ProgressBar value={uploadStatus.progress} />}
 *       {uploadFeedback && <FeedbackMessage {...uploadFeedback} />}
 *     </EvidenceUploadZone>
 *   );
 * }
 * ```
 */

'use client';

import { useState, useCallback, useRef } from 'react';
import {
  getPresignedUploadUrl,
  uploadToS3,
  notifyUploadComplete,
  type UploadProgress,
} from '@/lib/api/evidence';
import { logger } from '@/lib/logger';

// =============================================================================
// Types
// =============================================================================

export interface UploadStatus {
  isUploading: boolean;
  currentFile: string;
  progress: number;
  completed: number;
  total: number;
}

export type FeedbackTone = 'info' | 'success' | 'error';

export interface UploadFeedback {
  message: string;
  tone: FeedbackTone;
}

export interface UseEvidenceUploadOptions {
  /**
   * Callback fired when upload completes (success or partial success)
   * Use this to refresh the evidence list
   */
  onUploadComplete?: () => void;

  /**
   * Duration in milliseconds to show feedback message
   * @default 5000
   */
  feedbackDuration?: number;
}

export interface UseEvidenceUploadReturn {
  /**
   * Upload handler to be passed to the upload component
   */
  handleUpload: (files: File[]) => Promise<void>;

  /**
   * Current upload status with progress information
   */
  uploadStatus: UploadStatus;

  /**
   * Feedback message to display after upload
   */
  uploadFeedback: UploadFeedback | null;

  /**
   * Whether any upload is currently in progress
   */
  isUploading: boolean;

  /**
   * Clear the feedback message manually
   */
  clearFeedback: () => void;

  /**
   * Reset all upload state
   */
  reset: () => void;
}

// =============================================================================
// Constants
// =============================================================================

const DEFAULT_FEEDBACK_DURATION = 5000;

const INITIAL_UPLOAD_STATUS: UploadStatus = {
  isUploading: false,
  currentFile: '',
  progress: 0,
  completed: 0,
  total: 0,
};

// =============================================================================
// Hook
// =============================================================================

export function useEvidenceUpload(
  caseId: string,
  options?: UseEvidenceUploadOptions
): UseEvidenceUploadReturn {
  const { onUploadComplete, feedbackDuration = DEFAULT_FEEDBACK_DURATION } = options || {};

  const [uploadStatus, setUploadStatus] = useState<UploadStatus>(INITIAL_UPLOAD_STATUS);
  const [uploadFeedback, setUploadFeedback] = useState<UploadFeedback | null>(null);

  // Ref to track feedback timeout for cleanup
  const feedbackTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Clear any existing feedback timeout
  const clearFeedbackTimeout = useCallback(() => {
    if (feedbackTimeoutRef.current) {
      clearTimeout(feedbackTimeoutRef.current);
      feedbackTimeoutRef.current = null;
    }
  }, []);

  // Set feedback with auto-clear
  const setFeedbackWithTimeout = useCallback(
    (feedback: UploadFeedback) => {
      clearFeedbackTimeout();
      setUploadFeedback(feedback);

      feedbackTimeoutRef.current = setTimeout(() => {
        setUploadFeedback(null);
        feedbackTimeoutRef.current = null;
      }, feedbackDuration);
    },
    [clearFeedbackTimeout, feedbackDuration]
  );

  // Clear feedback manually
  const clearFeedback = useCallback(() => {
    clearFeedbackTimeout();
    setUploadFeedback(null);
  }, [clearFeedbackTimeout]);

  // Reset all state
  const reset = useCallback(() => {
    clearFeedbackTimeout();
    setUploadStatus(INITIAL_UPLOAD_STATUS);
    setUploadFeedback(null);
  }, [clearFeedbackTimeout]);

  // Main upload handler
  const handleUpload = useCallback(
    async (files: File[]) => {
      if (files.length === 0 || !caseId) return;

      // Initialize upload status
      setUploadStatus({
        isUploading: true,
        currentFile: files[0].name,
        progress: 0,
        completed: 0,
        total: files.length,
      });

      let successCount = 0;
      let failCount = 0;

      // Process each file
      for (let i = 0; i < files.length; i++) {
        const file = files[i];

        // Update current file
        setUploadStatus((prev) => ({
          ...prev,
          currentFile: file.name,
          progress: 0,
        }));

        try {
          // Step 1: Get presigned URL from backend
          const presignedResult = await getPresignedUploadUrl(
            caseId,
            file.name,
            file.type || 'application/octet-stream'
          );

          if (presignedResult.error || !presignedResult.data) {
            throw new Error(presignedResult.error || 'Failed to get presigned URL');
          }

          const { upload_url, evidence_temp_id, s3_key } = presignedResult.data;

          // Step 2: Upload directly to S3
          const uploadSuccess = await uploadToS3(upload_url, file, (progress: UploadProgress) => {
            setUploadStatus((prev) => ({
              ...prev,
              progress: progress.percent,
            }));
          });

          if (!uploadSuccess) {
            throw new Error('S3 upload failed');
          }

          // Step 3: Notify backend of completion
          const completeResult = await notifyUploadComplete({
            case_id: caseId,
            evidence_temp_id,
            s3_key,
            file_size: file.size,
          });

          if (completeResult.error) {
            throw new Error(completeResult.error || 'Failed to complete upload');
          }

          successCount++;
        } catch (error) {
          logger.error(`Upload failed for ${file.name}:`, error);
          failCount++;
        }

        // Update completed count
        setUploadStatus((prev) => ({
          ...prev,
          completed: i + 1,
        }));
      }

      // Mark upload as complete
      setUploadStatus((prev) => ({ ...prev, isUploading: false }));

      // Set appropriate feedback message
      if (failCount === 0) {
        setFeedbackWithTimeout({
          tone: 'success',
          message: `${successCount}개 파일 업로드 완료. AI가 증거를 분석 중입니다.`,
        });
        onUploadComplete?.();
      } else if (successCount > 0) {
        setFeedbackWithTimeout({
          tone: 'info',
          message: `${successCount}개 성공, ${failCount}개 실패. 실패한 파일을 다시 업로드해주세요.`,
        });
        onUploadComplete?.();
      } else {
        setFeedbackWithTimeout({
          tone: 'error',
          message: `업로드 실패. 네트워크를 확인하고 다시 시도해주세요.`,
        });
      }
    },
    [caseId, onUploadComplete, setFeedbackWithTimeout]
  );

  return {
    handleUpload,
    uploadStatus,
    uploadFeedback,
    isUploading: uploadStatus.isUploading,
    clearFeedback,
    reset,
  };
}

export default useEvidenceUpload;
