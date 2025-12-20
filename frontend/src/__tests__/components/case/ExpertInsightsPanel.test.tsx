/**
 * ExpertInsightsPanel Smoke Tests
 * refactor/lawyer-case-detail-ui
 *
 * Basic rendering and interaction tests for the expert insights modal.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { ExpertInsightsPanel } from '@/components/case/ExpertInsightsPanel';

describe('ExpertInsightsPanel', () => {
  const defaultProps = {
    isOpen: true,
    onClose: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('rendering', () => {
    it('should render when isOpen is true', () => {
      render(<ExpertInsightsPanel {...defaultProps} />);

      expect(screen.getByText('전문가 인사이트')).toBeInTheDocument();
    });

    it('should not render when isOpen is false', () => {
      render(<ExpertInsightsPanel isOpen={false} onClose={jest.fn()} />);

      expect(screen.queryByText('전문가 인사이트')).not.toBeInTheDocument();
    });

    it('should render property division section', () => {
      render(<ExpertInsightsPanel {...defaultProps} />);

      expect(screen.getByText('재산분할 원칙 (판례)')).toBeInTheDocument();
    });

    it('should render tax implications section', () => {
      render(<ExpertInsightsPanel {...defaultProps} />);

      expect(screen.getByText('세무/행정 유의사항')).toBeInTheDocument();
    });
  });

  describe('content sections', () => {
    it('should display special property information', () => {
      render(<ExpertInsightsPanel {...defaultProps} />);

      expect(screen.getByText('특유재산의 처리')).toBeInTheDocument();
    });

    it('should display retirement benefits information', () => {
      render(<ExpertInsightsPanel {...defaultProps} />);

      expect(screen.getByText('퇴직금 및 연금')).toBeInTheDocument();
    });

    it('should display fraudulent conveyance information', () => {
      render(<ExpertInsightsPanel {...defaultProps} />);

      expect(screen.getByText('사해행위 취소권')).toBeInTheDocument();
    });

    it('should display tax difference information', () => {
      render(<ExpertInsightsPanel {...defaultProps} />);

      expect(screen.getByText('위자료 vs 재산분할 세금 차이')).toBeInTheDocument();
    });
  });

  describe('close interactions', () => {
    it('should call onClose when close button is clicked', () => {
      render(<ExpertInsightsPanel {...defaultProps} />);

      const closeButton = screen.getByText('닫기');
      fireEvent.click(closeButton);

      expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
    });

    it('should call onClose when X button is clicked', () => {
      render(<ExpertInsightsPanel {...defaultProps} />);

      // X button is the one in the header (before the 닫기 button)
      const buttons = screen.getAllByRole('button');
      const xButton = buttons[0]; // First button is the X
      fireEvent.click(xButton);

      expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
    });

    it('should call onClose when backdrop is clicked', () => {
      render(<ExpertInsightsPanel {...defaultProps} />);

      // Find the backdrop (the outer overlay div)
      const backdrop = document.querySelector('.bg-black\\/50');
      if (backdrop) {
        fireEvent.click(backdrop);
      }

      expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('footer', () => {
    it('should display reference citation', () => {
      render(<ExpertInsightsPanel {...defaultProps} />);

      expect(screen.getByText(/2024 Household Litigation Guide/)).toBeInTheDocument();
    });
  });
});
