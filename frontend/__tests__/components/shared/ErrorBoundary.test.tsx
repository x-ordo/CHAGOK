/**
 * ErrorBoundary Component Tests
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  ErrorFallback,
  LawyerPortalError,
  ClientPortalError,
  DetectivePortalError,
  NetworkError,
  NotFoundError,
} from '@/components/shared/ErrorBoundary';

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  error: jest.fn(),
  __esModule: true,
  default: {
    error: jest.fn(),
  },
}));

// Mock window.location
const mockLocationHref = jest.fn();
Object.defineProperty(window, 'location', {
  value: {
    href: '',
    set href(value: string) {
      mockLocationHref(value);
    },
  },
  writable: true,
});

describe('ErrorFallback', () => {
  const mockError = new Error('Test error message');
  const mockReset = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders default title and description', () => {
    render(<ErrorFallback error={mockError} reset={mockReset} />);
    
    expect(screen.getByText('오류가 발생했습니다')).toBeInTheDocument();
    expect(screen.getByText('일시적인 문제가 발생했습니다. 잠시 후 다시 시도해 주세요.')).toBeInTheDocument();
  });

  it('renders custom title and description', () => {
    render(
      <ErrorFallback
        error={mockError}
        reset={mockReset}
        title="커스텀 제목"
        description="커스텀 설명"
      />
    );
    
    expect(screen.getByText('커스텀 제목')).toBeInTheDocument();
    expect(screen.getByText('커스텀 설명')).toBeInTheDocument();
  });

  it('calls reset when retry button is clicked', () => {
    render(<ErrorFallback error={mockError} reset={mockReset} />);
    
    fireEvent.click(screen.getByText('다시 시도'));
    
    expect(mockReset).toHaveBeenCalledTimes(1);
  });

  it('navigates to home when home button is clicked', () => {
    render(<ErrorFallback error={mockError} reset={mockReset} />);
    
    fireEvent.click(screen.getByText('홈으로 이동'));
    
    expect(mockLocationHref).toHaveBeenCalledWith('/');
  });
});

describe('Portal-specific Error Components', () => {
  const mockError = new Error('Test error');
  const mockReset = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('LawyerPortalError renders correct message', () => {
    render(<LawyerPortalError error={mockError} reset={mockReset} />);
    
    expect(screen.getByText('변호사 포털 오류')).toBeInTheDocument();
    expect(screen.getByText(/변호사 포털에서 오류가 발생했습니다/)).toBeInTheDocument();
  });

  it('ClientPortalError renders correct message', () => {
    render(<ClientPortalError error={mockError} reset={mockReset} />);
    
    expect(screen.getByText('의뢰인 포털 오류')).toBeInTheDocument();
    expect(screen.getByText(/의뢰인 포털에서 오류가 발생했습니다/)).toBeInTheDocument();
  });

  it('DetectivePortalError renders correct message', () => {
    render(<DetectivePortalError error={mockError} reset={mockReset} />);
    
    expect(screen.getByText('탐정 포털 오류')).toBeInTheDocument();
    expect(screen.getByText(/탐정 포털에서 오류가 발생했습니다/)).toBeInTheDocument();
  });
});

describe('NetworkError', () => {
  const mockReset = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders network error message', () => {
    render(<NetworkError reset={mockReset} />);
    
    expect(screen.getByText('네트워크 연결 오류')).toBeInTheDocument();
    expect(screen.getByText('인터넷 연결을 확인하고 다시 시도해 주세요.')).toBeInTheDocument();
  });

  it('calls reset when retry button is clicked', () => {
    render(<NetworkError reset={mockReset} />);
    
    fireEvent.click(screen.getByText('다시 시도'));
    
    expect(mockReset).toHaveBeenCalledTimes(1);
  });
});

describe('NotFoundError', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders 404 error message', () => {
    render(<NotFoundError />);
    
    expect(screen.getByText('페이지를 찾을 수 없습니다')).toBeInTheDocument();
    expect(screen.getByText(/요청하신 페이지가 존재하지 않거나 이동되었습니다/)).toBeInTheDocument();
  });

  it('navigates to home when button is clicked', () => {
    render(<NotFoundError />);
    
    fireEvent.click(screen.getByText('홈으로 이동'));
    
    expect(mockLocationHref).toHaveBeenCalledWith('/');
  });
});
