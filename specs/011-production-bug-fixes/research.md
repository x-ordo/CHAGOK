# Research: Production Login Bug Analysis

**Feature**: 011-production-bug-fixes
**Date**: 2025-12-11
**Purpose**: 로그인 후 대시보드 리다이렉트 실패 버그의 근본 원인 분석

## Executive Summary

로그인 버그는 **Cross-Origin 쿠키 전달 문제**와 **Race Condition** 두 가지 원인으로 발생할 수 있다. 기존 코드에서 Race Condition은 이미 부분적으로 수정되었으나 (JUST_LOGGED_IN_KEY 플래그), Production 환경의 Cross-Origin 쿠키 설정에 문제가 있을 가능성이 높다.

## Authentication Flow Analysis

### Current Architecture

```
┌─────────────────┐     POST /auth/login      ┌─────────────────┐
│   LoginForm.tsx │ ──────────────────────────▶ │  Backend API    │
│   (CloudFront)  │                            │  (Separate Host) │
└────────┬────────┘                            └────────┬────────┘
         │                                              │
         │ ◀─────────────────────────────────────────── │
         │     Response + Set-Cookie (HTTP-only)        │
         │                                              │
         ▼
┌─────────────────────────────────────────┐
│ AuthContext.login():                    │
│  1. sessionStorage.setItem(JUST_LOGGED_IN) │
│  2. localStorage.setItem(USER_CACHE)    │
│  3. document.cookie = user_data         │
│  4. router.push(dashboardPath)          │
└─────────────────────────────────────────┘
         │
         ▼ Page Navigation
┌─────────────────────────────────────────┐
│ AuthProvider Mount:                     │
│  - Check JUST_LOGGED_IN_KEY            │
│  - If true: Load from cache (SKIP API)  │
│  - If false: Call GET /auth/me          │
└─────────────────────────────────────────┘
```

### Key Files

| File | Role | Lines of Interest |
|------|------|-------------------|
| `backend/app/api/auth.py` | JWT 토큰 생성, 쿠키 설정 | 36-86 (cookie helpers), 89-130 (login) |
| `backend/app/core/config.py` | CORS, Cookie 설정 | COOKIE_SAMESITE, COOKIE_SECURE |
| `frontend/src/contexts/AuthContext.tsx` | 인증 상태 관리 | 110-127 (race condition fix), 137-194 (login) |
| `frontend/src/middleware.ts` | 라우트 보호 | 140-149 (authenticated redirect), 153-164 (protected routes) |
| `frontend/src/lib/api/client.ts` | HTTP 클라이언트 | 44 (credentials: 'include') |

## Root Cause Investigation

### Investigation 1: Cross-Origin Cookie Transmission

**Problem**: CloudFront (frontend)와 API (backend)가 다른 도메인에서 호스팅될 때, HTTP-only 쿠키가 전달되지 않을 수 있음.

**Requirements for Cross-Origin Cookies**:
1. `SameSite=None` (cross-site 요청 허용)
2. `Secure=True` (HTTPS 필수)
3. `credentials: 'include'` (fetch 요청)
4. Backend CORS에 프론트엔드 origin 포함

**Current Settings** (from code analysis):
```python
# backend/app/api/auth.py
COOKIE_SECURE = settings.cookie_secure        # config에서 가져옴
COOKIE_SAMESITE = settings.cookie_samesite    # config에서 가져옴
COOKIE_DOMAIN = settings.cookie_domain        # config에서 가져옴
```

**Decision**: Cross-Origin 환경에서 쿠키 전달을 위해 설정 검증 및 수정 필요
**Rationale**: Production 환경에서 CloudFront와 API가 다른 도메인이면 올바른 쿠키 설정 필수
**Alternatives Considered**:
- localStorage 기반 토큰 → XSS 취약, 거부
- API Gateway 프록시 → 복잡도 증가, 보류

### Investigation 2: Race Condition

**Problem**: 로그인 후 router.push() 호출 시, 새 페이지의 AuthProvider가 마운트되면서 checkAuth()가 호출됨. 이 때 쿠키가 아직 설정되지 않았거나, API 응답을 기다리는 동안 인증 상태가 false로 평가되어 로그인 페이지로 리다이렉트됨.

**Existing Fix** (commit 8de802d):
```typescript
// AuthContext.tsx
const justLoggedIn = sessionStorage.getItem(JUST_LOGGED_IN_KEY);
if (justLoggedIn === 'true') {
  sessionStorage.removeItem(JUST_LOGGED_IN_KEY);
  const cachedUser = localStorage.getItem(USER_CACHE_KEY);
  if (cachedUser) {
    setUser(JSON.parse(cachedUser));
    setIsLoading(false);
    return; // Skip checkAuth()
  }
}
```

**Decision**: 기존 수정이 충분한지 검증, 필요시 강화
**Rationale**: sessionStorage 플래그 접근은 동기적이므로 race condition 방지에 효과적
**Alternatives Considered**:
- Promise.all로 상태 저장 완료 대기 → 불필요한 복잡도
- URL 파라미터로 로그인 상태 전달 → 보안 위험

### Investigation 3: Middleware Cookie Sync

**Problem**: Next.js middleware는 서버 사이드에서 실행되며, HTTP-only 쿠키(`access_token`)에 직접 접근 불가. 대신 `user_data` 공개 쿠키를 사용하지만, 이 쿠키와 실제 세션 상태가 불일치할 수 있음.

**Current Implementation**:
```typescript
// middleware.ts
const userDataCookie = request.cookies.get('user_data');
if (!userDataCookie?.value) {
  // Redirect to login
}
```

**Decision**: user_data 쿠키 동기화 로직 검증
**Rationale**: Middleware는 초기 라우팅에만 사용, 실제 인증은 API 호출로 검증
**Alternatives Considered**:
- JWT를 미들웨어에서 직접 검증 → HTTP-only 쿠키라 불가능
- API route로 인증 확인 → 추가 네트워크 요청, 느림

## Recommended Fix Strategy

### Priority 1: Cookie Configuration Verification

1. Production 환경 변수 확인:
   ```
   COOKIE_SAMESITE=none
   COOKIE_SECURE=true
   CORS_ORIGINS=https://dpbf86zqulqfy.cloudfront.net
   ```

2. Backend `auth.py` 쿠키 설정 검증:
   ```python
   response.set_cookie(
       key="access_token",
       value=access_token,
       httponly=True,
       secure=True,           # HTTPS 환경
       samesite="none",       # Cross-origin
       path="/",
       domain=None,           # 자동 감지
       max_age=...
   )
   ```

### Priority 2: Race Condition Hardening

1. Login 메서드에서 상태 저장 순서 확인:
   ```typescript
   // 1. 먼저 모든 상태 저장 (동기)
   sessionStorage.setItem(JUST_LOGGED_IN_KEY, 'true');
   localStorage.setItem(USER_CACHE_KEY, JSON.stringify(userData));
   document.cookie = `user_data=${...}`;

   // 2. 그 다음 리다이렉트 (비동기)
   await router.push(dashboardPath);
   ```

2. AuthProvider에서 JUST_LOGGED_IN_KEY 체크 강화

### Priority 3: Middleware/Auth State Sync

1. Login 성공 시 user_data 쿠키 올바르게 설정
2. Logout 시 모든 쿠키/스토리지 일관되게 정리

## Testing Strategy

### Unit Tests (Jest)

```typescript
describe('Login Flow', () => {
  it('should redirect to dashboard after successful login', async () => {
    // Mock API response
    // Verify router.push called with correct path
  });

  it('should maintain auth state after page refresh', async () => {
    // Setup authenticated state
    // Simulate page refresh
    // Verify user state preserved
  });

  it('should redirect authenticated user from /login to dashboard', async () => {
    // Setup authenticated state
    // Navigate to /login
    // Verify redirect to dashboard
  });
});
```

### E2E Tests (Playwright)

```typescript
test('complete login flow', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // Should redirect to dashboard
  await expect(page).toHaveURL(/\/lawyer\/dashboard/);

  // Refresh should maintain state
  await page.reload();
  await expect(page).toHaveURL(/\/lawyer\/dashboard/);
});
```

## Conclusion

| Root Cause | Likelihood | Fix Complexity | Priority |
|------------|------------|----------------|----------|
| Cross-Origin Cookie Config | High | Low | P1 |
| Race Condition | Medium | Already Fixed | P2 (Verify) |
| Middleware Sync | Low | Low | P3 |

**Recommended Approach**:
1. 먼저 Production 환경의 쿠키 설정 검증 (브라우저 DevTools Network 탭)
2. 쿠키가 전달되지 않으면 Backend 설정 수정
3. 쿠키가 전달되면 Race Condition 재검증
