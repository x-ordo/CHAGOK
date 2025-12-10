# Implementation Plan: MVP 구현 갭 해소 (Production Readiness)

**Branch**: `009-mvp-gap-closure` | **Date**: 2025-12-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-mvp-gap-closure/spec.md`

## Summary

MVP 출시를 위한 구현 갭 해소. 11개 User Story로 구성되며, AI Worker 배포, Backend RAG/Draft API, Frontend 에러 처리, CI 정상화, 권한 제어, 법적 고지, 역할별 포털 기능을 포함. 기존 코드베이스 활용하여 missing pieces 구현에 집중.

## Technical Context

**Language/Version**: Python 3.11+ (Backend/AI Worker), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, Next.js 14, OpenAI (GPT-4o, Whisper), Qdrant, boto3, TipTap
**Storage**: PostgreSQL (RDS), AWS S3, DynamoDB, Qdrant Cloud
**Testing**: pytest (80% coverage), Jest + React Testing Library, Playwright (E2E)
**Target Platform**: AWS (Lambda, S3, CloudFront, RDS)
**Project Type**: Web application (3-tier: Frontend + Backend + AI Worker)
**Performance Goals**: Draft Preview < 30s, RAG search < 2s, Evidence processing < 5min
**Constraints**: 500MB max file upload, JWT 24h expiry, S3 presigned URL 5min expiry
**Scale/Scope**: MVP launch, 3 user roles (lawyer/client/detective), case-level isolation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Evidence Integrity | ✅ PASS | SHA-256 hash + audit_logs already designed |
| II. Case Isolation | ✅ PASS | `case_rag_{case_id}` pattern in spec |
| III. No Auto-Submit | ✅ PASS | Draft Preview is "미리보기" only |
| IV. AWS-Only Storage | ✅ PASS | S3/DynamoDB/Qdrant within AWS |
| V. Clean Architecture | ✅ PASS | Router→Service→Repository pattern |
| VI. Branch Protection | ✅ PASS | PR-based workflow enforced |
| VII. TDD Cycle | ⚠️ PARTIAL | Existing tests, TDD for new features |
| VIII. Semantic Versioning | ✅ PASS | v0.2.0 tagged, following SemVer |

**Gate Status**: PASS (proceed to Phase 0)

## Project Structure

### Documentation (this feature)

```text
specs/009-mvp-gap-closure/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI specs)
│   ├── signup-api.yaml
│   ├── client-portal-api.yaml
│   ├── detective-portal-api.yaml
│   └── evidence-review-api.yaml
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/              # Route handlers
│   │   ├── auth.py       # US9: role selection in signup
│   │   ├── cases.py      # US5,10,11: permission checks
│   │   ├── evidence.py   # US10,11: status, EXIF extraction
│   │   └── detective_portal.py  # US11: earnings
│   ├── services/
│   │   ├── auth_service.py      # Role-based redirect
│   │   ├── evidence_service.py  # Review workflow
│   │   └── exif_service.py      # NEW: EXIF metadata extraction
│   ├── repositories/
│   │   ├── evidence_repository.py
│   │   └── detective_earnings_repository.py  # NEW
│   └── middleware/
│       └── permission_middleware.py  # US5: case-level checks
└── tests/

frontend/
├── src/
│   ├── app/
│   │   ├── signup/page.tsx      # US9: role dropdown
│   │   ├── client/              # US10: client portal
│   │   └── detective/           # US11: detective portal
│   ├── components/
│   │   ├── auth/
│   │   └── shared/
│   ├── hooks/
│   │   └── useAuth.ts           # Role-based redirect
│   └── lib/
│       └── api/
└── src/__tests__/

ai_worker/
├── handler.py                   # S3 event processing
├── src/
│   ├── parsers/                 # File type parsers
│   └── storage/                 # DynamoDB + Qdrant
└── tests/
```

**Structure Decision**: Web application (Option 2) - existing 3-tier architecture maintained

## Complexity Tracking

> No Constitution violations requiring justification

## Implementation Phases

### Phase 1: P1 Features (AI Worker + RAG/Draft)
- US1: AI Worker Lambda deployment with S3 triggers
- US2: RAG search API + Draft Preview API

### Phase 2: P2 Features (Core MVP)
- US3: Frontend error handling unification
- US4: CI test coverage normalization
- US5: Case permission middleware
- US7: Legal notices (ToS, Privacy)
- US9: Signup role selection
- US10: Client portal evidence upload
- US11: Detective portal EXIF + earnings

### Phase 3: P3 Features (Polish)
- US6: Deployment pipeline (staging/prod)
- US8: Information Architecture improvements
