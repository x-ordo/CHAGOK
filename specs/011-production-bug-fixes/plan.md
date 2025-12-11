# Implementation Plan: Production Bug Fixes

**Branch**: `011-production-bug-fixes` | **Date**: 2025-12-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/011-production-bug-fixes/spec.md`

## Summary

로그인 성공 후 대시보드로 리다이렉트되지 않고 로그인 페이지로 돌아가는 버그를 수정한다. HTTP-only 쿠키 기반 JWT 인증 시스템에서 프론트엔드-백엔드 간 쿠키 전달 문제와 race condition을 분석하고 해결한다. 프론트엔드 우선 접근으로 시작하되 필요시 백엔드도 수정 가능.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, Next.js 14, jose (JWT), Tailwind CSS
**Storage**: PostgreSQL (RDS), HTTP-only Cookies (JWT 토큰)
**Testing**: pytest (Backend), Jest + React Testing Library (Frontend)
**Target Platform**: AWS CloudFront (Frontend), AWS EC2/Lambda (Backend API)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: 로그인→대시보드 3초 이내 (SC-003)
**Constraints**: HTTP-only 쿠키 사용 (XSS 방지), Cross-origin 환경 (CloudFront ↔ API)
**Scale/Scope**: 3 user roles (lawyer, client, detective), 단일 로그인 버그 수정

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Evidence Integrity | N/A | 이 기능은 증거 처리와 무관 |
| II. Case Isolation | N/A | 인증은 케이스 레벨 이전에 발생 |
| III. No Auto-Submit | N/A | AI 출력 없음 |
| IV. AWS-Only Storage | ✅ | HTTP-only 쿠키 사용 (브라우저 내장 저장) |
| V. Clean Architecture | ✅ | 기존 구조 유지 (Routers → Services) |
| VI. Branch Protection | ✅ | feat/* 브랜치에서 작업, PR 통해 dev → main |
| VII. TDD Cycle | ✅ | 버그 수정 전 테스트 작성 |
| VIII. Semantic Versioning | ✅ | PATCH 버전으로 릴리스 (버그 수정) |

**Gate Status**: ✅ PASSED - No violations

## Project Structure

### Documentation (this feature)

```text
specs/011-production-bug-fixes/
├── plan.md              # This file
├── research.md          # Phase 0 output - Auth flow analysis
├── data-model.md        # Phase 1 output - Auth state entities
├── quickstart.md        # Phase 1 output - Verification steps
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   └── auth.py           # 로그인 API, 쿠키 설정
│   └── core/
│       ├── security.py       # JWT 생성/검증
│       └── config.py         # CORS, Cookie 설정
└── tests/
    └── contract/
        └── test_auth.py      # 인증 계약 테스트

frontend/
├── src/
│   ├── app/
│   │   └── login/page.tsx    # 로그인 페이지
│   ├── components/
│   │   └── auth/
│   │       └── LoginForm.tsx # 로그인 폼 컴포넌트
│   ├── contexts/
│   │   └── AuthContext.tsx   # 인증 상태 관리
│   ├── hooks/
│   │   └── useAuth.ts        # 인증 훅
│   ├── lib/
│   │   └── api/
│   │       ├── auth.ts       # 인증 API 클라이언트
│   │       └── client.ts     # HTTP 클라이언트 (credentials)
│   └── middleware.ts         # 라우트 보호
└── src/__tests__/
    └── auth/
        └── login-flow.test.tsx  # 로그인 플로우 테스트
```

**Structure Decision**: Web application (frontend + backend) - 기존 LEH 프로젝트 구조 유지

## Implementation Phases

### Phase 1: Diagnosis & Fix (Critical Path)

1. **Cross-Origin Cookie Investigation**
   - Production 환경에서 CloudFront → API 간 쿠키 전달 검증
   - `credentials: 'include'` 설정 확인
   - CORS_ORIGINS, COOKIE_SAMESITE, COOKIE_SECURE 설정 검증

2. **Race Condition 검증**
   - JUST_LOGGED_IN_KEY sessionStorage 플래그 동작 확인
   - router.push() 전에 모든 상태가 저장되는지 검증

3. **Fix Implementation**
   - 식별된 근본 원인에 따른 수정
   - Frontend: AuthContext, middleware
   - Backend (필요시): Cookie 설정, CORS 설정

### Phase 2: Verification & Testing

1. **TDD 테스트 작성**
   - 로그인 → 대시보드 리다이렉트 플로우 테스트
   - 페이지 새로고침 후 상태 유지 테스트
   - 뒤로가기 버튼 처리 테스트

2. **E2E 테스트 (Playwright)**
   - Production URL에서 실제 로그인 플로우 테스트

## Complexity Tracking

> No Constitution violations to justify

## Key Investigation Points

Based on the auth flow research, focus areas for debugging:

| Area | Files | Potential Issue |
|------|-------|-----------------|
| Cookie Domain | `backend/app/api/auth.py:54,80,85` | COOKIE_DOMAIN이 production domain과 불일치 가능 |
| Cross-Origin | `backend/app/core/config.py` | SameSite=None + Secure=True 필요 (HTTPS cross-origin) |
| Middleware Sync | `frontend/src/middleware.ts:158-164` | user_data 쿠키와 실제 세션 상태 불일치 가능 |
| Race Condition | `frontend/src/contexts/AuthContext.tsx:182` | router.push() 전 sessionStorage 저장 완료 필요 |
