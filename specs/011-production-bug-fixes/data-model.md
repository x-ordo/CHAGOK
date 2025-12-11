# Data Model: Authentication State

**Feature**: 011-production-bug-fixes
**Date**: 2025-12-11

## Overview

이 문서는 로그인 버그 수정에 관련된 인증 상태 엔티티들을 정의한다. 버그 수정 자체는 기존 엔티티를 변경하지 않으며, 상태 동기화 로직만 수정한다.

## Entities

### 1. User (Backend - PostgreSQL)

기존 사용자 모델. 버그 수정에서 변경 없음.

```python
class User(Base):
    __tablename__ = "users"

    id: str              # UUID, primary key
    email: str           # unique
    name: str
    role: UserRole       # LAWYER | CLIENT | DETECTIVE
    status: UserStatus   # ACTIVE | INACTIVE | PENDING
    hashed_password: str
    created_at: datetime
    updated_at: datetime
```

### 2. JWT Payload (Backend → Frontend)

JWT 토큰에 포함되는 클레임.

```typescript
interface JWTPayload {
  sub: string;           // user_id
  exp: number;           // expiration timestamp
  iat: number;           // issued at timestamp
  type?: "refresh";      // refresh 토큰만 해당
}
```

### 3. AuthUser (Frontend State)

프론트엔드에서 관리하는 사용자 상태.

```typescript
interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: "lawyer" | "client" | "detective";
  status: "active" | "inactive" | "pending";
}
```

### 4. AuthState (Frontend Context)

AuthContext에서 관리하는 전체 인증 상태.

```typescript
interface AuthState {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;  // computed: user !== null
}
```

## Storage Locations

| Data | Storage Type | Accessibility | Purpose |
|------|--------------|---------------|---------|
| `access_token` | HTTP-only Cookie | Backend only | API 인증 |
| `refresh_token` | HTTP-only Cookie (path=/auth) | Backend only | 토큰 갱신 |
| `user_data` | Public Cookie | Frontend + Middleware | 라우트 보호 |
| `USER_CACHE_KEY` | localStorage | Frontend only | Race condition 방지 |
| `JUST_LOGGED_IN_KEY` | sessionStorage | Frontend only | Race condition 플래그 |
| `AuthUser` | React Context | Frontend only | UI 렌더링 |

## State Transitions

### Login Flow

```
[Unauthenticated]
    │
    ▼ POST /auth/login (success)
    │
[Cookies Set by Backend]
    │
    ▼ Frontend: Set localStorage + sessionStorage
    │
[Authenticated + JUST_LOGGED_IN flag]
    │
    ▼ router.push(dashboard)
    │
[New Page Mount]
    │
    ▼ AuthProvider: Check JUST_LOGGED_IN
    │
    ├─── true: Load from localStorage, clear flag
    │          → [Authenticated (from cache)]
    │
    └─── false: Call GET /auth/me
               ├─── success: [Authenticated]
               └─── failure: [Unauthenticated]
```

### Logout Flow

```
[Authenticated]
    │
    ▼ POST /auth/logout
    │
[Backend: Clear cookies]
    │
    ▼ Frontend: Clear all storage
    │
[Unauthenticated]
```

## Cookie Configuration

### access_token (HTTP-only)

```
Set-Cookie: access_token=<jwt>;
  HttpOnly;
  Secure;
  SameSite=None;
  Path=/;
  Max-Age=86400
```

### refresh_token (HTTP-only)

```
Set-Cookie: refresh_token=<jwt>;
  HttpOnly;
  Secure;
  SameSite=None;
  Path=/auth;
  Max-Age=604800
```

### user_data (Public)

```
Set-Cookie: user_data=<encoded_json>;
  Path=/;
  Max-Age=86400
```

**Note**: `SameSite=None`은 cross-origin 환경 (CloudFront ↔ API)에서 필수. `Secure=true`와 함께 사용해야 함.

## Validation Rules

| Field | Rule |
|-------|------|
| JWT `exp` | 현재 시간보다 미래여야 함 |
| JWT `sub` | 유효한 user_id (DB에 존재) |
| User `role` | "lawyer" \| "client" \| "detective" 중 하나 |
| User `status` | "active"만 로그인 허용 |

## Role-based Dashboard Mapping

```typescript
const DASHBOARD_PATHS: Record<UserRole, string> = {
  lawyer: "/lawyer/dashboard",
  client: "/client/dashboard",
  detective: "/detective/dashboard",
};
```

## Changes Required for Bug Fix

이 버그 수정은 데이터 모델 자체를 변경하지 않음. 변경 대상:

1. **Cookie Configuration**: SameSite, Secure 설정 검증/수정
2. **State Sync Logic**: localStorage/sessionStorage 저장 순서
3. **Middleware Logic**: user_data 쿠키 파싱 및 리다이렉트
