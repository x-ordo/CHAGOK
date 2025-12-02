/**
 * Login Page
 * Plan 3.19.2 - Routing Structure Change
 *
 * Features:
 * - Login form (moved from root `/`)
 * - Redirect to `/cases` if already authenticated (via HTTP-only cookie)
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import LoginForm from '@/components/auth/LoginForm';
import { getCurrentUser } from '@/lib/api/auth';

export default function LoginPage() {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Navigation Guard: Check if already authenticated via cookie
    const checkAuth = async () => {
      try {
        const response = await getCurrentUser();
        if (response.data && !response.error) {
          // Already authenticated, redirect to cases
          router.replace('/cases');
          return;
        }
      } catch {
        // Not authenticated, show login form
      }
      setIsChecking(false);
    };

    checkAuth();
  }, [router]);

  // Show loading while checking auth
  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="text-gray-500">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-deep-trust-blue mb-2">
            Legal Evidence Hub
          </h1>
          <p className="text-neutral-600">로그인하여 시작하세요</p>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}
