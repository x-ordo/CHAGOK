/**
 * LoadingButton Component Tests
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { LoadingButton } from '@/components/shared/LoadingButton';

describe('LoadingButton', () => {
  it('renders children correctly', () => {
    render(<LoadingButton>저장</LoadingButton>);
    expect(screen.getByRole('button')).toHaveTextContent('저장');
  });

  it('shows spinner when loading', () => {
    render(<LoadingButton isLoading>저장</LoadingButton>);
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-busy', 'true');
    // Spinner SVG should be present
    expect(button.querySelector('svg')).toBeInTheDocument();
  });

  it('shows loading text when provided', () => {
    render(
      <LoadingButton isLoading loadingText="저장 중...">
        저장
      </LoadingButton>
    );
    expect(screen.getByRole('button')).toHaveTextContent('저장 중...');
  });

  it('is disabled when loading', () => {
    render(<LoadingButton isLoading>저장</LoadingButton>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('is disabled when disabled prop is true', () => {
    render(<LoadingButton disabled>저장</LoadingButton>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('calls onClick when clicked and not loading', () => {
    const handleClick = jest.fn();
    render(<LoadingButton onClick={handleClick}>저장</LoadingButton>);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', () => {
    const handleClick = jest.fn();
    render(
      <LoadingButton disabled onClick={handleClick}>
        저장
      </LoadingButton>
    );
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('does not call onClick when loading', () => {
    const handleClick = jest.fn();
    render(
      <LoadingButton isLoading onClick={handleClick}>
        저장
      </LoadingButton>
    );
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('applies variant classes correctly', () => {
    const { rerender } = render(<LoadingButton variant="primary">버튼</LoadingButton>);
    expect(screen.getByRole('button')).toHaveClass('bg-primary');

    rerender(<LoadingButton variant="danger">버튼</LoadingButton>);
    expect(screen.getByRole('button')).toHaveClass('bg-error');

    rerender(<LoadingButton variant="secondary">버튼</LoadingButton>);
    expect(screen.getByRole('button')).toHaveClass('bg-neutral-200');
  });

  it('applies size classes correctly', () => {
    const { rerender } = render(<LoadingButton size="sm">버튼</LoadingButton>);
    expect(screen.getByRole('button')).toHaveClass('px-3', 'py-1.5');

    rerender(<LoadingButton size="lg">버튼</LoadingButton>);
    expect(screen.getByRole('button')).toHaveClass('px-6', 'py-3');
  });

  it('applies fullWidth class when specified', () => {
    render(<LoadingButton fullWidth>버튼</LoadingButton>);
    expect(screen.getByRole('button')).toHaveClass('w-full');
  });

  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLButtonElement>();
    render(<LoadingButton ref={ref}>버튼</LoadingButton>);
    expect(ref.current).toBeInstanceOf(HTMLButtonElement);
  });

  it('has correct displayName', () => {
    expect(LoadingButton.displayName).toBe('LoadingButton');
  });
});
