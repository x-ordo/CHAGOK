/**
 * DraftGenerationModal Accessibility Tests
 * TDD Red → Green cycle for button accessibility (plan.md Section 7)
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import DraftGenerationModal from '@/components/draft/DraftGenerationModal';

describe('DraftGenerationModal Accessibility', () => {
  const defaultProps = {
    isOpen: true,
    onClose: jest.fn(),
    onGenerate: jest.fn(),
    hasFactSummary: true,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Button type="button" attribute', () => {
    it('close button (X icon) should have type="button"', () => {
      render(<DraftGenerationModal {...defaultProps} />);

      const closeButton = screen.getByRole('button', { name: '닫기' });
      expect(closeButton).toHaveAttribute('type', 'button');
    });

    it('cancel button should have type="button"', () => {
      render(<DraftGenerationModal {...defaultProps} />);

      const cancelButton = screen.getByRole('button', { name: '취소' });
      expect(cancelButton).toHaveAttribute('type', 'button');
    });

    it('generate button should have type="button"', () => {
      render(<DraftGenerationModal {...defaultProps} />);

      const generateButton = screen.getByRole('button', { name: /초안 생성/i });
      expect(generateButton).toHaveAttribute('type', 'button');
    });

    it('all buttons in modal should have type="button"', () => {
      render(<DraftGenerationModal {...defaultProps} />);

      const allButtons = screen.getAllByRole('button');
      allButtons.forEach((button) => {
        expect(button).toHaveAttribute('type', 'button');
      });
    });
  });

  describe('aria-label accessibility', () => {
    it('close button should have aria-label="닫기"', () => {
      render(<DraftGenerationModal {...defaultProps} />);

      const closeButton = screen.getByRole('button', { name: '닫기' });
      expect(closeButton).toHaveAttribute('aria-label', '닫기');
    });
  });

  describe('Modal rendering', () => {
    it('should not render when isOpen is false', () => {
      render(<DraftGenerationModal {...defaultProps} isOpen={false} />);

      expect(screen.queryByText('초안 생성')).not.toBeInTheDocument();
    });

    it('should render modal title when isOpen is true', () => {
      render(<DraftGenerationModal {...defaultProps} />);

      expect(screen.getByRole('heading', { name: '초안 생성' })).toBeInTheDocument();
    });
  });
});
