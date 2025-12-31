/**
 * useRole Hook Tests
 */

import React from 'react';
import { renderHook } from '@testing-library/react';
import { useRole } from '@/hooks/useRole';

// Mock useAuth hook
const mockUseAuth = jest.fn();
jest.mock('@/hooks/useAuth', () => ({
  useAuth: () => mockUseAuth(),
}));

// Mock user types
jest.mock('@/types/user', () => ({
  hasFeatureAccess: jest.fn((role, feature) => {
    const accessMap: Record<string, string[]> = {
      admin: ['cases', 'billing', 'settings', 'admin'],
      lawyer: ['cases', 'billing', 'settings'],
      staff: ['cases'],
      client: ['my-case'],
      detective: ['reports'],
    };
    return accessMap[role]?.includes(feature) ?? false;
  }),
  getDashboardPath: jest.fn((role) => {
    const paths: Record<string, string> = {
      admin: '/admin/dashboard',
      lawyer: '/lawyer/dashboard',
      staff: '/staff/dashboard',
      client: '/client/dashboard',
      detective: '/detective/dashboard',
    };
    return paths[role] || '/login';
  }),
  getPortalPath: jest.fn((role) => {
    const paths: Record<string, string> = {
      admin: '/admin',
      lawyer: '/lawyer',
      staff: '/lawyer',
      client: '/client',
      detective: '/detective',
    };
    return paths[role] || '/';
  }),
  isInternalUser: jest.fn((role) => ['admin', 'lawyer', 'staff'].includes(role)),
  isExternalUser: jest.fn((role) => ['client', 'detective'].includes(role)),
  ROLE_DISPLAY_NAMES: {
    admin: '관리자',
    lawyer: '변호사',
    staff: '직원',
    client: '의뢰인',
    detective: '탐정',
  },
}));

describe('useRole', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset localStorage mock
    (global.localStorage.getItem as jest.Mock).mockReturnValue(null);
  });

  it('returns null values when not authenticated', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      role: null,
      isAuthenticated: false,
      isLoading: false,
    });

    const { result } = renderHook(() => useRole());

    expect(result.current.user).toBeNull();
    expect(result.current.role).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.isAdmin).toBe(false);
    expect(result.current.isLawyer).toBe(false);
  });

  it('identifies admin role correctly', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'Admin', role: 'admin' },
      role: 'admin',
      isAuthenticated: true,
      isLoading: false,
    });

    const { result } = renderHook(() => useRole());

    expect(result.current.isAdmin).toBe(true);
    expect(result.current.isLawyer).toBe(false);
    expect(result.current.isInternal).toBe(true);
    expect(result.current.isExternal).toBe(false);
    expect(result.current.roleDisplayName).toBe('관리자');
  });

  it('identifies lawyer role correctly', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '2', name: 'Lawyer', role: 'lawyer' },
      role: 'lawyer',
      isAuthenticated: true,
      isLoading: false,
    });

    const { result } = renderHook(() => useRole());

    expect(result.current.isLawyer).toBe(true);
    expect(result.current.isAdmin).toBe(false);
    expect(result.current.isInternal).toBe(true);
    expect(result.current.dashboardPath).toBe('/lawyer/dashboard');
    expect(result.current.portalPath).toBe('/lawyer');
  });

  it('identifies client role correctly', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '3', name: 'Client', role: 'client' },
      role: 'client',
      isAuthenticated: true,
      isLoading: false,
    });

    const { result } = renderHook(() => useRole());

    expect(result.current.isClient).toBe(true);
    expect(result.current.isExternal).toBe(true);
    expect(result.current.isInternal).toBe(false);
  });

  it('hasAccess returns correct values', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '2', name: 'Lawyer', role: 'lawyer' },
      role: 'lawyer',
      isAuthenticated: true,
      isLoading: false,
    });

    const { result } = renderHook(() => useRole());

    expect(result.current.hasAccess('cases')).toBe(true);
    expect(result.current.hasAccess('billing')).toBe(true);
    expect(result.current.hasAccess('admin')).toBe(false);
  });

  it('canAccessPortal returns correct values for admin', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '1', name: 'Admin', role: 'admin' },
      role: 'admin',
      isAuthenticated: true,
      isLoading: false,
    });

    const { result } = renderHook(() => useRole());

    expect(result.current.canAccessPortal('admin')).toBe(true);
    expect(result.current.canAccessPortal('lawyer')).toBe(true);
    expect(result.current.canAccessPortal('client')).toBe(true);
    expect(result.current.canAccessPortal('detective')).toBe(true);
  });

  it('canAccessPortal returns correct values for lawyer', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '2', name: 'Lawyer', role: 'lawyer' },
      role: 'lawyer',
      isAuthenticated: true,
      isLoading: false,
    });

    const { result } = renderHook(() => useRole());

    expect(result.current.canAccessPortal('lawyer')).toBe(true);
    expect(result.current.canAccessPortal('admin')).toBe(false);
    expect(result.current.canAccessPortal('client')).toBe(false);
  });

  it('canAccessPortal returns correct values for client', () => {
    mockUseAuth.mockReturnValue({
      user: { id: '3', name: 'Client', role: 'client' },
      role: 'client',
      isAuthenticated: true,
      isLoading: false,
    });

    const { result } = renderHook(() => useRole());

    expect(result.current.canAccessPortal('client')).toBe(true);
    expect(result.current.canAccessPortal('lawyer')).toBe(false);
    expect(result.current.canAccessPortal('admin')).toBe(false);
  });

  it('returns loading state correctly', () => {
    mockUseAuth.mockReturnValue({
      user: null,
      role: null,
      isAuthenticated: false,
      isLoading: true,
    });

    const { result } = renderHook(() => useRole());

    expect(result.current.isLoading).toBe(true);
  });
});
