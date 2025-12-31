/**
 * EmptyState Component Tests
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { EmptyState, ErrorState } from '@/components/shared/EmptyState';

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Inbox: () => <svg data-testid="inbox-icon" />,
  FileText: () => <svg data-testid="file-icon" />,
  FolderOpen: () => <svg data-testid="folder-icon" />,
  Search: () => <svg data-testid="search-icon" />,
  Plus: () => <svg data-testid="plus-icon" />,
}));

// Mock Button component
jest.mock('@/components/primitives', () => ({
  Button: ({ children, onClick, variant }: any) => (
    <button onClick={onClick} data-variant={variant}>
      {children}
    </button>
  ),
}));

describe('EmptyState', () => {
  it('renders title correctly', () => {
    render(<EmptyState title="데이터가 없습니다" />);
    expect(screen.getByRole('status')).toHaveAttribute('aria-label', '데이터가 없습니다');
    expect(screen.getByText('데이터가 없습니다')).toBeInTheDocument();
  });

  it('renders description when provided', () => {
    render(
      <EmptyState
        title="데이터가 없습니다"
        description="새 항목을 추가해 보세요."
      />
    );
    expect(screen.getByText('새 항목을 추가해 보세요.')).toBeInTheDocument();
  });

  it('renders different icon types', () => {
    const { rerender } = render(<EmptyState title="테스트" icon="inbox" />);
    expect(screen.getByTestId('inbox-icon')).toBeInTheDocument();

    rerender(<EmptyState title="테스트" icon="file" />);
    expect(screen.getByTestId('file-icon')).toBeInTheDocument();

    rerender(<EmptyState title="테스트" icon="folder" />);
    expect(screen.getByTestId('folder-icon')).toBeInTheDocument();

    rerender(<EmptyState title="테스트" icon="search" />);
    expect(screen.getByTestId('search-icon')).toBeInTheDocument();
  });

  it('renders custom icon when provided', () => {
    const CustomIcon = () => <span data-testid="custom-icon">Custom</span>;
    render(
      <EmptyState title="테스트" icon="custom" customIcon={<CustomIcon />} />
    );
    expect(screen.getByTestId('custom-icon')).toBeInTheDocument();
  });

  it('renders primary action button', () => {
    const handleClick = jest.fn();
    render(
      <EmptyState
        title="데이터가 없습니다"
        primaryAction={{
          label: '새로 만들기',
          onClick: handleClick,
        }}
      />
    );
    const button = screen.getByText('새로 만들기');
    expect(button).toBeInTheDocument();
    fireEvent.click(button);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('renders secondary action button', () => {
    const handleClick = jest.fn();
    render(
      <EmptyState
        title="데이터가 없습니다"
        secondaryAction={{
          label: '도움말',
          onClick: handleClick,
        }}
      />
    );
    const button = screen.getByText('도움말');
    expect(button).toBeInTheDocument();
    fireEvent.click(button);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('renders children content', () => {
    render(
      <EmptyState title="테스트">
        <div data-testid="child-content">커스텀 컨텐츠</div>
      </EmptyState>
    );
    expect(screen.getByTestId('child-content')).toBeInTheDocument();
  });

  it('applies size classes correctly', () => {
    const { rerender, container } = render(<EmptyState title="테스트" size="sm" />);
    expect(container.firstChild).toHaveClass('py-8');

    rerender(<EmptyState title="테스트" size="md" />);
    expect(container.firstChild).toHaveClass('py-12');

    rerender(<EmptyState title="테스트" size="lg" />);
    expect(container.firstChild).toHaveClass('py-16');
  });

  it('applies custom className', () => {
    const { container } = render(
      <EmptyState title="테스트" className="custom-class" />
    );
    expect(container.firstChild).toHaveClass('custom-class');
  });
});

describe('ErrorState', () => {
  it('renders with default values', () => {
    render(<ErrorState />);
    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText('오류가 발생했습니다')).toBeInTheDocument();
    expect(screen.getByText('데이터를 불러오는 중 문제가 발생했습니다.')).toBeInTheDocument();
  });

  it('renders custom title and message', () => {
    render(
      <ErrorState
        title="네트워크 오류"
        message="서버에 연결할 수 없습니다."
      />
    );
    expect(screen.getByText('네트워크 오류')).toBeInTheDocument();
    expect(screen.getByText('서버에 연결할 수 없습니다.')).toBeInTheDocument();
  });

  it('renders retry button when onRetry is provided', () => {
    const handleRetry = jest.fn();
    render(<ErrorState onRetry={handleRetry} />);
    const button = screen.getByText('다시 시도');
    expect(button).toBeInTheDocument();
    fireEvent.click(button);
    expect(handleRetry).toHaveBeenCalledTimes(1);
  });

  it('renders custom retry text', () => {
    render(<ErrorState onRetry={() => {}} retryText="재시도" />);
    expect(screen.getByText('재시도')).toBeInTheDocument();
  });

  it('does not render retry button when onRetry is not provided', () => {
    render(<ErrorState />);
    expect(screen.queryByText('다시 시도')).not.toBeInTheDocument();
  });

  it('applies size classes correctly', () => {
    const { rerender, container } = render(<ErrorState size="sm" />);
    expect(container.firstChild).toHaveClass('py-6');

    rerender(<ErrorState size="md" />);
    expect(container.firstChild).toHaveClass('py-10');

    rerender(<ErrorState size="lg" />);
    expect(container.firstChild).toHaveClass('py-14');
  });
});
