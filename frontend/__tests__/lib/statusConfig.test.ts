/**
 * Status Config Tests
 */

import {
  getCaseStatusConfig,
  getEvidenceStatusConfig,
  getCaseStatusBadgeClasses,
  getEvidenceStatusBadgeClasses,
  getCaseStatusLabel,
  getEvidenceStatusLabel,
  CASE_STATUS_COLORS,
  CASE_STATUS_LABELS,
  EVIDENCE_STATUS_COLORS,
  EVIDENCE_STATUS_LABELS,
} from '@/lib/utils/statusConfig';

describe('Case Status Config', () => {
  describe('getCaseStatusConfig', () => {
    it('returns correct config for active status', () => {
      const config = getCaseStatusConfig('active');
      expect(config.label).toBe('활성');
      expect(config.color).toContain('blue');
    });

    it('returns correct config for closed status', () => {
      const config = getCaseStatusConfig('closed');
      expect(config.label).toBe('종료');
      expect(config.color).toContain('gray');
    });

    it('returns correct config for in_progress status', () => {
      const config = getCaseStatusConfig('in_progress');
      expect(config.label).toBe('검토 대기');
      expect(config.color).toContain('yellow');
    });

    it('returns default config for unknown status', () => {
      const config = getCaseStatusConfig('unknown');
      expect(config.label).toBe('unknown');
      expect(config.color).toBe(CASE_STATUS_COLORS.active);
    });
  });

  describe('getCaseStatusBadgeClasses', () => {
    it('returns correct classes for known status', () => {
      expect(getCaseStatusBadgeClasses('active')).toContain('blue');
      expect(getCaseStatusBadgeClasses('pending')).toContain('yellow');
      expect(getCaseStatusBadgeClasses('blocked')).toContain('red');
    });

    it('returns default classes for unknown status', () => {
      expect(getCaseStatusBadgeClasses('unknown')).toBe(CASE_STATUS_COLORS.active);
    });
  });

  describe('getCaseStatusLabel', () => {
    it('returns correct label for known status', () => {
      expect(getCaseStatusLabel('active')).toBe('활성');
      expect(getCaseStatusLabel('open')).toBe('진행 중');
      expect(getCaseStatusLabel('completed')).toBe('완료');
    });

    it('returns status itself for unknown status', () => {
      expect(getCaseStatusLabel('custom_status')).toBe('custom_status');
    });
  });
});

describe('Evidence Status Config', () => {
  describe('getEvidenceStatusConfig', () => {
    it('returns correct config for verified status', () => {
      const config = getEvidenceStatusConfig('verified');
      expect(config.label).toBe('검증완료');
      expect(config.color).toContain('green');
    });

    it('returns correct config for processing status', () => {
      const config = getEvidenceStatusConfig('processing');
      expect(config.label).toBe('처리중');
      expect(config.color).toContain('purple');
    });

    it('returns correct config for failed status', () => {
      const config = getEvidenceStatusConfig('failed');
      expect(config.label).toBe('실패');
      expect(config.color).toContain('red');
    });

    it('returns default config for unknown status', () => {
      const config = getEvidenceStatusConfig('unknown');
      expect(config.label).toBe('처리중');
      expect(config.color).toContain('gray');
    });
  });

  describe('getEvidenceStatusBadgeClasses', () => {
    it('returns correct classes for known status', () => {
      expect(getEvidenceStatusBadgeClasses('verified')).toContain('green');
      expect(getEvidenceStatusBadgeClasses('pending_review')).toContain('yellow');
      expect(getEvidenceStatusBadgeClasses('rejected')).toContain('red');
    });

    it('returns default classes for unknown status', () => {
      expect(getEvidenceStatusBadgeClasses('unknown')).toContain('gray');
    });
  });

  describe('getEvidenceStatusLabel', () => {
    it('returns correct label for known status', () => {
      expect(getEvidenceStatusLabel('verified')).toBe('검증완료');
      expect(getEvidenceStatusLabel('processed')).toBe('분석완료');
      expect(getEvidenceStatusLabel('queued')).toBe('대기열');
    });

    it('returns default label for unknown status', () => {
      expect(getEvidenceStatusLabel('custom_status')).toBe('처리중');
    });
  });
});

describe('Status Constants', () => {
  it('CASE_STATUS_COLORS has all required statuses', () => {
    const requiredStatuses = ['active', 'open', 'in_progress', 'closed', 'pending', 'review', 'completed', 'blocked', 'waiting'];
    requiredStatuses.forEach(status => {
      expect(CASE_STATUS_COLORS).toHaveProperty(status);
    });
  });

  it('CASE_STATUS_LABELS has all required statuses', () => {
    const requiredStatuses = ['active', 'open', 'in_progress', 'closed', 'pending', 'review', 'completed', 'blocked', 'waiting'];
    requiredStatuses.forEach(status => {
      expect(CASE_STATUS_LABELS).toHaveProperty(status);
    });
  });

  it('EVIDENCE_STATUS_COLORS has all required statuses', () => {
    const requiredStatuses = ['verified', 'approved', 'processed', 'pending_review', 'rejected', 'processing', 'queued', 'uploading', 'failed'];
    requiredStatuses.forEach(status => {
      expect(EVIDENCE_STATUS_COLORS).toHaveProperty(status);
    });
  });

  it('EVIDENCE_STATUS_LABELS has all required statuses', () => {
    const requiredStatuses = ['verified', 'approved', 'processed', 'pending_review', 'rejected', 'processing', 'queued', 'uploading', 'failed'];
    requiredStatuses.forEach(status => {
      expect(EVIDENCE_STATUS_LABELS).toHaveProperty(status);
    });
  });
});
