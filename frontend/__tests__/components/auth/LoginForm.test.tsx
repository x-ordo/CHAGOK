/**
 * LoginForm Component Tests
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginForm from '@/components/auth/LoginForm';

// Mock useAuth hook
const mockLogin = jest.fn();
jest.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    login: mockLogin,
  }),
}));

// Mock primitives
jest.mock('@/components/primitives', () => ({
  Button: ({ children, onClick, type, isLoading, loadingText, fullWidth, variant }: any) => (
    <button
      type={type}
      onClick={onClick}
      disabled={isLoading}
      data-variant={variant}
      data-fullwidth={fullWidth}
    >
      {isLoading ? loadingText : children}
    </button>
  ),
  Input: ({ id, type, label, value, onChange, error, required }: any) => (
    <div>
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        required={required}
        aria-invalid={!!error}
      />
      {error && <span role="alert">{error}</span>}
    </div>
  ),
}));

describe('LoginForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders email and password inputs', () => {
    render(<LoginForm />);
    expect(screen.getByLabelText('이메일')).toBeInTheDocument();
    expect(screen.getByLabelText('비밀번호')).toBeInTheDocument();
  });

  it('renders login button', () => {
    render(<LoginForm />);
    expect(screen.getByRole('button', { name: '로그인' })).toBeInTheDocument();
  });

  it('renders forgot password link', () => {
    render(<LoginForm />);
    expect(screen.getByText('비밀번호를 잊으셨나요?')).toBeInTheDocument();
  });

  it('updates email input value', async () => {
    render(<LoginForm />);
    const emailInput = screen.getByLabelText('이메일');
    
    await userEvent.type(emailInput, 'test@example.com');
    
    expect(emailInput).toHaveValue('test@example.com');
  });

  it('updates password input value', async () => {
    render(<LoginForm />);
    const passwordInput = screen.getByLabelText('비밀번호');
    
    await userEvent.type(passwordInput, 'password123');
    
    expect(passwordInput).toHaveValue('password123');
  });

  it('calls login on form submit with correct credentials', async () => {
    mockLogin.mockResolvedValue({ success: true });
    
    render(<LoginForm />);
    
    await userEvent.type(screen.getByLabelText('이메일'), 'test@example.com');
    await userEvent.type(screen.getByLabelText('비밀번호'), 'password123');
    
    fireEvent.submit(screen.getByRole('button', { name: '로그인' }).closest('form')!);
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });

  it('shows error message on login failure', async () => {
    mockLogin.mockResolvedValue({ success: false, error: '잘못된 자격 증명' });
    
    render(<LoginForm />);
    
    await userEvent.type(screen.getByLabelText('이메일'), 'test@example.com');
    await userEvent.type(screen.getByLabelText('비밀번호'), 'wrongpassword');
    
    fireEvent.submit(screen.getByRole('button', { name: '로그인' }).closest('form')!);
    
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('잘못된 자격 증명');
    });
  });

  it('shows default error message when no specific error', async () => {
    mockLogin.mockResolvedValue({ success: false });
    
    render(<LoginForm />);
    
    await userEvent.type(screen.getByLabelText('이메일'), 'test@example.com');
    await userEvent.type(screen.getByLabelText('비밀번호'), 'wrongpassword');
    
    fireEvent.submit(screen.getByRole('button', { name: '로그인' }).closest('form')!);
    
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('아이디 또는 비밀번호를 확인해 주세요.');
    });
  });

  it('shows error on exception during login', async () => {
    mockLogin.mockRejectedValue(new Error('Network error'));
    
    render(<LoginForm />);
    
    await userEvent.type(screen.getByLabelText('이메일'), 'test@example.com');
    await userEvent.type(screen.getByLabelText('비밀번호'), 'password123');
    
    fireEvent.submit(screen.getByRole('button', { name: '로그인' }).closest('form')!);
    
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('로그인 중 오류가 발생했습니다.');
    });
  });

  it('shows loading state during login', async () => {
    // Create a promise that doesn't resolve immediately
    let resolveLogin: (value: any) => void;
    mockLogin.mockReturnValue(new Promise((resolve) => {
      resolveLogin = resolve;
    }));
    
    render(<LoginForm />);
    
    await userEvent.type(screen.getByLabelText('이메일'), 'test@example.com');
    await userEvent.type(screen.getByLabelText('비밀번호'), 'password123');
    
    fireEvent.submit(screen.getByRole('button').closest('form')!);
    
    // Should show loading state
    await waitFor(() => {
      expect(screen.getByRole('button')).toHaveTextContent('로그인 중...');
      expect(screen.getByRole('button')).toBeDisabled();
    });
    
    // Resolve the login
    resolveLogin!({ success: true });
  });
});
