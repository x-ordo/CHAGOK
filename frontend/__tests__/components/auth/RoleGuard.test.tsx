/**
 * RoleGuard Component Tests
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { RoleGuard, AccessDenied } from '@/components/auth/RoleGuard';

// Mock next/navigation
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

// Mock useRole hook
const mockUseRole = jest.fn();
jest.mock('@/hooks/useRole', () => ({
  useRole: () => mockUseRole(),
}));

describe('RoleGuard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders children when user has required role', async () => {
    mockUseRole.mockReturnValue({
      user: { id: '1', name: 'Lawyer' },
      role: 'lawyer',
      isAuthenticated: true,
      hasAccess: () => true,
      isLoading: false,
    });

    render(
      <RoleGuard allowedRoles={['lawyer']}>
        <div data-testid="protected-content">Protected Content</div>
      </RoleGuard>
    );

    await waitFor(() => {
      expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    });
  });

  it('shows loading state while checking auth', () => {
    mockUseRole.mockReturnValue({
      user: null,
      role: null,
      isAuthenticated: false,
      hasAccess: () => false,
      isLoading: true,
    });

    const { container } = render(
      <RoleGuard allowedRoles={['lawyer']}>
        <div>Protected Content</div>
      </RoleGuard>
    );

    expect(container.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('redirects when user is not authenticated', async () => {
    mockUseRole.mockReturnValue({
      user: null,
      role: null,
      isAuthenticated: false,
      hasAccess: () => false,
      isLoading: false,
    });

    render(
      <RoleGuard allowedRoles={['lawyer']}>
        <div>Protected Content</div>
      </RoleGuard>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/login');
    });
  });

  it('redirects to custom path when specified', async () => {
    mockUseRole.mockReturnValue({
      user: null,
      role: null,
      isAuthenticated: false,
      hasAccess: () => false,
      isLoading: false,
    });

    render(
      <RoleGuard allowedRoles={['admin']} redirectTo="/unauthorized">
        <div>Protected Content</div>
      </RoleGuard>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/unauthorized');
    });
  });

  it('redirects when user does not have required role', async () => {
    mockUseRole.mockReturnValue({
      user: { id: '1', name: 'Client' },
      role: 'client',
      isAuthenticated: true,
      hasAccess: () => false,
      isLoading: false,
    });

    render(
      <RoleGuard allowedRoles={['lawyer', 'admin']}>
        <div>Protected Content</div>
      </RoleGuard>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/login');
    });
  });

  it('renders fallback when user lacks access', async () => {
    mockUseRole.mockReturnValue({
      user: { id: '1', name: 'Client' },
      role: 'client',
      isAuthenticated: true,
      hasAccess: () => false,
      isLoading: false,
    });

    render(
      <RoleGuard
        allowedRoles={['lawyer']}
        fallback={<div data-testid="fallback">Access Denied</div>}
      >
        <div>Protected Content</div>
      </RoleGuard>
    );

    await waitFor(() => {
      expect(screen.getByTestId('fallback')).toBeInTheDocument();
    });
    expect(mockPush).not.toHaveBeenCalled();
  });

  it('checks feature access when requiredFeature is specified', async () => {
    const mockHasAccess = jest.fn().mockReturnValue(true);
    mockUseRole.mockReturnValue({
      user: { id: '1', name: 'Lawyer' },
      role: 'lawyer',
      isAuthenticated: true,
      hasAccess: mockHasAccess,
      isLoading: false,
    });

    render(
      <RoleGuard requiredFeature="billing">
        <div data-testid="protected-content">Billing Content</div>
      </RoleGuard>
    );

    await waitFor(() => {
      expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    });
  });

  it('redirects when user lacks required feature', async () => {
    mockUseRole.mockReturnValue({
      user: { id: '1', name: 'Staff' },
      role: 'staff',
      isAuthenticated: true,
      hasAccess: () => false,
      isLoading: false,
    });

    render(
      <RoleGuard requiredFeature="admin">
        <div>Admin Content</div>
      </RoleGuard>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/login');
    });
  });

  it('does not show loading when showLoading is false', () => {
    mockUseRole.mockReturnValue({
      user: null,
      role: null,
      isAuthenticated: false,
      hasAccess: () => false,
      isLoading: true,
    });

    const { container } = render(
      <RoleGuard allowedRoles={['lawyer']} showLoading={false}>
        <div>Protected Content</div>
      </RoleGuard>
    );

    expect(container.querySelector('.animate-spin')).not.toBeInTheDocument();
  });
});

describe('AccessDenied', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseRole.mockReturnValue({
      dashboardPath: '/lawyer/dashboard',
      roleDisplayName: '변호사',
    });
  });

  it('renders access denied message', () => {
    render(<AccessDenied />);
    
    expect(screen.getByText('접근 권한이 없습니다')).toBeInTheDocument();
    expect(screen.getByText(/변호사 역할로는 이 페이지에 접근할 수 없습니다/)).toBeInTheDocument();
  });

  it('renders custom message when provided', () => {
    render(<AccessDenied message="커스텀 에러 메시지" />);
    
    expect(screen.getByText('커스텀 에러 메시지')).toBeInTheDocument();
  });

  it('navigates to dashboard on button click', () => {
    render(<AccessDenied />);
    
    const button = screen.getByText('대시보드로 이동');
    button.click();
    
    expect(mockPush).toHaveBeenCalledWith('/lawyer/dashboard');
  });
});
