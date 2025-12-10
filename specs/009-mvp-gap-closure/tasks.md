# Tasks: MVP 구현 갭 해소 (Production Readiness)

**Input**: Design documents from `/specs/009-mvp-gap-closure/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested - test tasks included only where necessary for CI coverage (US4).

**Organization**: Tasks grouped by user story. Most features are 70-100% complete - tasks focus on configuration, integration, and polish.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`
- **Frontend**: `frontend/src/`
- **AI Worker**: `ai_worker/`
- **CI/CD**: `.github/workflows/`

---

## Phase 1: Setup (Verification)

**Purpose**: Verify existing implementation state before making changes

- [ ] T001 Verify AWS CLI is configured with correct credentials
- [ ] T002 [P] Verify OpenAI API key is set in environment
- [ ] T003 [P] Verify Qdrant Cloud instance is accessible
- [ ] T004 Run `git checkout 009-mvp-gap-closure` to ensure on correct branch

---

## Phase 2: Foundational (AWS Infrastructure)

**Purpose**: AWS configuration that MUST be complete before US1 can function

**⚠️ CRITICAL**: AI Worker cannot process files until this phase is complete

- [ ] T005 Create S3 bucket `leh-evidence-dev` via AWS CLI: `aws s3 mb s3://leh-evidence-dev --region ap-northeast-2`
- [ ] T006 [P] Create S3 bucket `leh-evidence-prod` via AWS CLI: `aws s3 mb s3://leh-evidence-prod --region ap-northeast-2`
- [ ] T007 Attach S3 policy to Lambda execution role `leh-ai-worker-role`
- [ ] T008 Configure S3 event notification on `leh-evidence-dev` to trigger `leh-ai-worker` Lambda
- [ ] T009 [P] Configure S3 event notification on `leh-evidence-prod` to trigger production Lambda
- [ ] T010 Verify Lambda function `leh-ai-worker` exists and has correct handler

**Checkpoint**: S3 → Lambda trigger chain is complete - US1 can now function

---

## Phase 3: User Story 1 - AI Worker 실서비스 연동 (Priority: P1) 🎯 MVP

**Goal**: Evidence files uploaded to S3 automatically trigger AI analysis

**Independent Test**: Upload file to `s3://leh-evidence-dev/cases/test-case/raw/test.jpg` and verify DynamoDB record created

### Implementation for User Story 1

- [ ] T011 [US1] Test S3 upload triggers Lambda by uploading test file via AWS CLI
- [ ] T012 [US1] Verify DynamoDB table `leh_evidence_dev` receives analysis results
- [ ] T013 [US1] Verify Qdrant collection `case_rag_{case_id}` receives embeddings
- [ ] T014 [US1] Check CloudWatch logs for Lambda execution success
- [ ] T015 [US1] Document S3 path pattern in `docs/guides/EVIDENCE_UPLOAD.md`

**Checkpoint**: AI Worker is fully operational - files are processed automatically

---

## Phase 4: User Story 2 - Backend RAG 검색 및 Draft 생성 (Priority: P1) 🎯 MVP

**Goal**: RAG search and Draft Preview APIs work with real data

**Independent Test**: Call `POST /cases/{id}/draft-preview` and verify AI-generated draft with citations

### Implementation for User Story 2

> **Note**: Backend RAG/Draft is 90-95% complete. Tasks focus on verification and minor fixes.

- [ ] T016 [US2] Verify `GET /search?q={query}&case_id={id}` returns Qdrant results in `backend/app/api/search.py`
- [ ] T017 [US2] Verify `POST /cases/{id}/draft-preview` generates draft with citations in `backend/app/api/drafts.py`
- [ ] T018 [US2] Verify `GET /cases/{id}/draft-export` generates DOCX/PDF in `backend/app/services/draft_service.py`
- [ ] T019 [US2] Test draft generation with real case data (requires US1 complete)
- [ ] T019a [US2] Integrate TipTap editor for draft editing in `frontend/src/components/draft/DraftEditor.tsx` (FR-007a)
- [ ] T020 [US2] Add smoke test for RAG search in `backend/tests/integration/test_search_smoke.py`

**Checkpoint**: RAG search and Draft generation work with AI Worker processed data

---

## Phase 5: User Story 3 - Frontend 에러 처리 통일 (Priority: P2)

**Goal**: Consistent error handling across all frontend components

**Independent Test**: Simulate network error and verify toast notification appears with retry option

### Implementation for User Story 3

- [ ] T021 [US3] Install react-hot-toast: `cd frontend && npm install react-hot-toast`
- [ ] T022 [US3] Add Toaster component to `frontend/src/app/layout.tsx`
- [ ] T023 [P] [US3] Add toast notifications to API client error handling in `frontend/src/lib/api/client.ts`
- [ ] T024 [P] [US3] Create useRetry hook with exponential backoff in `frontend/src/hooks/useRetry.ts`
- [ ] T025 [US3] Unify loading state naming (isLoading) across hooks in `frontend/src/hooks/`
- [ ] T026 [US3] Add toast for 403 errors (permission denied) in `frontend/src/lib/api/client.ts`
- [ ] T027 [US3] Add toast for 500 errors (server error) in `frontend/src/lib/api/client.ts`
- [ ] T028 [US3] Update error boundary components to use toast in `frontend/src/components/shared/ErrorBoundary.tsx`

**Checkpoint**: All API errors show user-friendly toast notifications with retry options

---

## Phase 6: User Story 4 - CI 테스트 커버리지 정상화 (Priority: P2)

**Goal**: CI enforces test coverage and all tests actually run

**Independent Test**: Create PR and verify CI runs 300+ tests with 80%+ coverage

### Implementation for User Story 4

- [ ] T029 [US4] Update backend coverage threshold to 80% in `backend/pytest.ini` (Constitution requirement)
- [ ] T030 [P] [US4] Update ai_worker coverage threshold to 80% in `ai_worker/pytest.ini` (Constitution requirement)
- [ ] T031 [US4] Fix conftest.py skip logic in `ai_worker/tests/conftest.py` - skip only integration tests on missing env vars
- [ ] T032 [P] [US4] Add unit tests for draft_service.py in `backend/tests/unit/test_draft_service.py`
- [ ] T033 [P] [US4] Add unit tests for search_service.py in `backend/tests/unit/test_search_service.py`
- [ ] T034 [P] [US4] Add unit tests for qdrant.py in `backend/tests/unit/test_qdrant_client.py`
- [ ] T035 [US4] Verify CI workflow runs tests without skipping in `.github/workflows/ci.yml`
- [ ] T036 [US4] Run `pytest --cov=app --cov-report=term-missing` locally and fix coverage gaps

**Checkpoint**: CI enforces 80% coverage (Constitution requirement), all 300+ tests run without skips

---

## Phase 7: User Story 5 - 사건별 권한 제어 (Priority: P2)

**Goal**: All case-related APIs enforce membership and log access attempts

**Independent Test**: Call `/cases/{id}/evidence` without membership and verify 403 response + audit log

### Implementation for User Story 5

- [ ] T037 [US5] Audit `/cases/*` endpoints for permission checks in `backend/app/api/cases.py`
- [ ] T038 [P] [US5] Audit `/evidence/*` endpoints for permission checks in `backend/app/api/evidence.py`
- [ ] T039 [P] [US5] Audit `/drafts/*` endpoints for permission checks in `backend/app/api/drafts.py`
- [ ] T040 [US5] Ensure 403 (not 404) on unauthorized access across all audited endpoints
- [ ] T041 [US5] Add audit_log write for ACCESS_DENIED in `backend/app/services/audit_log_service.py`
- [ ] T042 [US5] Add permission check middleware in `backend/app/middleware/case_permission.py`
- [ ] T043 [US5] Add contract test for 403 response in `backend/tests/contract/test_permission_403.py`

**Checkpoint**: Unauthorized access returns 403 and is logged in audit_logs table

---

## Phase 8: User Story 6 - 기본 배포 파이프라인 (Priority: P3)

**Goal**: All components deploy automatically on merge

**Independent Test**: Merge to dev and verify staging deployment completes within 10 minutes

### Implementation for User Story 6

- [ ] T044 [US6] Enable AI Worker deployment in `.github/workflows/deploy_paralegal.yml` (remove `&& false`)
- [ ] T045 [US6] Verify AI Worker Dockerfile exists at `ai_worker/Dockerfile.lambda`
- [ ] T046 [US6] Add health check endpoint to AI Worker if missing
- [ ] T047 [P] [US6] Document manual rollback procedure in `docs/guides/ROLLBACK.md`
- [ ] T048 [P] [US6] Add deployment status badge to README.md
- [ ] T049 [US6] Test staging deployment by merging small change to dev branch
- [ ] T050 [US6] Verify CloudFront invalidation completes after frontend deploy

**Checkpoint**: All components (Backend, Frontend, AI Worker) deploy on merge to dev/main

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

- [ ] T051 [P] Update CLAUDE.md with new technologies and recent changes
- [ ] T052 [P] Run quickstart.md validation steps end-to-end
- [ ] T053 [P] Update API documentation in `docs/specs/API_SPEC.md` if endpoints changed
- [ ] T054 Create PR from `009-mvp-gap-closure` to `dev` with full changelog
- [ ] T055 Merge PR after review and verify staging deployment

---

## Phase 10: Observability (Priority: P3 - Deferred)

**Purpose**: NFR-001~003 implementation - Deferred post-MVP

> **Note**: Basic CloudWatch logging is enabled by default. These tasks enhance observability.

- [ ] T056 [P] [NFR] Configure structured JSON logging for Lambda in `ai_worker/handler.py`
- [ ] T057 [P] [NFR] Add CloudWatch custom metrics for Lambda execution in `ai_worker/src/observability/metrics.py`
- [ ] T058 [P] [NFR] Add API latency logging middleware in `backend/app/middleware/latency.py`
- [ ] T059 [NFR] Create CloudWatch dashboard for monitoring (AWS Console)

**Checkpoint**: Observability dashboard shows Lambda metrics and API latency percentiles

---

## Phase 11: User Story 7 - 법적 고지 및 약관 (Priority: P2)

**Goal**: Copyright notice, Terms of Service, Privacy Policy, and registration consent

**Independent Test**: Complete signup with terms agreement, verify footer copyright text

### Implementation for User Story 7

- [ ] T060 [P] [US7] Add copyright footer component in `frontend/src/components/shared/Footer.tsx`
- [ ] T061 [P] [US7] Create Terms of Service page at `frontend/src/app/terms/page.tsx`
- [ ] T062 [P] [US7] Create Privacy Policy page at `frontend/src/app/privacy/page.tsx`
- [ ] T063 [US7] Add terms/privacy agreement checkboxes to signup form in `frontend/src/app/signup/page.tsx`
- [ ] T064 [US7] Create `user_agreements` table migration in `backend/alembic/versions/`
- [ ] T065 [US7] Create UserAgreement model in `backend/app/db/models.py`
- [ ] T066 [US7] Update signup API to record agreement in `backend/app/api/auth.py`
- [ ] T067 [US7] Add agreement validation - block signup without consent
- [ ] T068 [US7] Draft Terms of Service content (Korean) in `frontend/public/legal/terms-ko.md`
- [ ] T069 [US7] Draft Privacy Policy content (PIPA compliant) in `frontend/public/legal/privacy-ko.md`

**Checkpoint**: Signup requires terms agreement, footer shows copyright, legal pages accessible

---

## Phase 12: User Story 8 - 정보 구조(IA) 개선 (Priority: P3)

**Goal**: Improve navigation structure for better usability

**Independent Test**: Access all major features within 3 clicks from dashboard

### Implementation for User Story 8

- [ ] T070 [P] [US8] Audit current navigation structure in `frontend/src/components/layout/`
- [ ] T071 [US8] Update main navigation to 1-depth for key features in `frontend/src/components/layout/Sidebar.tsx`
- [ ] T072 [US8] Add tab/sidebar navigation to case detail page in `frontend/src/app/lawyer/cases/[id]/page.tsx`
- [ ] T073 [US8] Ensure consistent back/home button behavior across all pages
- [ ] T074 [US8] Create IA documentation in `docs/guides/INFORMATION_ARCHITECTURE.md`

**Checkpoint**: 3-click access to all major features verified, consistent navigation

---

## Phase 14: User Story 9 - 회원가입 역할 선택 (Priority: P2)

**Goal**: Users select their role (lawyer/client/detective) during signup and redirect to role-specific dashboard

**Independent Test**: Complete signup with "client" role, verify redirect to `/client/dashboard`

### Implementation for User Story 9

- [ ] T082 [P] [US9] Add role dropdown to signup form in `frontend/src/app/signup/page.tsx`
- [ ] T083 [P] [US9] Update signup API call to include role parameter in `frontend/src/lib/api/auth.ts`
- [ ] T084 [US9] Verify backend accepts role in `POST /auth/signup` in `backend/app/api/auth.py`
- [ ] T085 [US9] Implement role-based redirect in middleware `frontend/src/middleware.ts`
- [ ] T086 [US9] Add validation - block signup without role selection
- [ ] T087 [US9] Test signup → login → redirect flow for each role (lawyer, client, detective)

**Checkpoint**: Users can register with role selection and land on role-specific dashboard

---

## Phase 15: User Story 10 - 의뢰인(Client) 포털 기능 (Priority: P2)

**Goal**: Clients can view their cases, upload evidence (pending review), and message lawyers

**Independent Test**: Login as client, upload evidence, verify status shows "검토 대기"

### Implementation for User Story 10

- [ ] T088 [P] [US10] Verify client can only see assigned cases via `case_members` in `backend/app/api/cases.py`
- [ ] T089 [P] [US10] Add `review_status` field to evidence upload response in `backend/app/api/evidence.py`
- [ ] T090 [US10] Update evidence upload to set `pending_review` for client uploads in `backend/app/services/evidence_service.py`
- [ ] T091 [US10] Create evidence review endpoint `PATCH /cases/{id}/evidence/{eid}/review` in `backend/app/api/evidence.py`
- [ ] T092 [US10] Add evidence review UI for lawyers in `frontend/src/components/lawyer/EvidenceReviewCard.tsx`
- [ ] T093 [P] [US10] Update client evidence list to show review status in `frontend/src/app/client/cases/[id]/page.tsx`
- [ ] T094 [US10] Add contract test for client evidence upload in `backend/tests/contract/test_client_evidence.py`
- [ ] T095 [US10] Verify 403 for client accessing non-assigned cases

**Checkpoint**: Clients can upload evidence (pending review), lawyers can approve/reject

---

## Phase 16: User Story 11 - 탐정(Detective) 포털 기능 (Priority: P2)

**Goal**: Detectives can view assigned cases, upload evidence with EXIF extraction, and check earnings

**Independent Test**: Upload image with GPS data, verify location metadata is extracted and displayed

### Implementation for User Story 11

- [ ] T096 [P] [US11] Create `exif_service.py` for metadata extraction in `backend/app/services/exif_service.py`
- [ ] T097 [P] [US11] Create `detective_earnings` table migration in `backend/alembic/versions/xxx_add_detective_earnings.py`
- [ ] T098 [US11] Create DetectiveEarnings model in `backend/app/db/models.py`
- [ ] T099 [US11] Create DetectiveEarningsRepository in `backend/app/repositories/detective_earnings_repository.py`
- [ ] T100 [US11] Create earnings API endpoints in `backend/app/api/detective_portal.py`
- [ ] T101 [US11] Extract EXIF on evidence upload for image files in `backend/app/services/evidence_service.py`
- [ ] T102 [P] [US11] Update detective earnings page to show data in `frontend/src/app/detective/earnings/page.tsx`
- [ ] T103 [P] [US11] Add EXIF metadata display to evidence detail in `frontend/src/components/detective/EvidenceMetadata.tsx`
- [ ] T104 [US11] Add contract test for EXIF extraction in `backend/tests/contract/test_exif_extraction.py`
- [ ] T105 [US11] Verify 403 for detective accessing non-assigned cases

**Checkpoint**: Detectives see EXIF data on uploads, earnings page shows case-based income

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS US1
- **Phase 3 (US1)**: Depends on Phase 2 (AWS infrastructure)
- **Phase 4 (US2)**: Depends on Phase 3 (needs AI-processed data for realistic testing)
- **Phase 5 (US3)**: Can start after Phase 1 - independent
- **Phase 6 (US4)**: Can start after Phase 1 - independent
- **Phase 7 (US5)**: Can start after Phase 1 - independent
- **Phase 8 (US6)**: Can start after Phase 1 - independent (but recommend after US1)
- **Phase 9 (Polish)**: Depends on all user stories complete
- **Phase 10 (Observability)**: Can start after Phase 1 - independent, but deferred to P3
- **Phase 11 (US7)**: Can start after Phase 1 - independent (P2 priority, pre-deployment required)
- **Phase 12 (US8)**: Can start after Phase 1 - independent (P3 priority, UX improvement)
- **Phase 13 (Refactoring)**: Can start after Phase 1 - independent (P2 priority, code quality)
- **Phase 14 (US9)**: Can start after Phase 1 - independent (P2 priority, role signup)
- **Phase 15 (US10)**: Depends on Phase 14 (US9) - client portal needs role signup
- **Phase 16 (US11)**: Depends on Phase 14 (US9) - detective portal needs role signup

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|------------|---------------------|
| US1 (AI Worker) | Phase 2 (AWS) | - |
| US2 (RAG/Draft) | US1 (needs data) | - |
| US3 (Error Handling) | Phase 1 only | US4, US5, US6, US7, US8, US9, US10, US11 |
| US4 (CI Tests) | Phase 1 only | US3, US5, US6, US7, US8, US9, US10, US11 |
| US5 (Permissions) | Phase 1 only | US3, US4, US6, US7, US8, US9, US10, US11 |
| US6 (Deployment) | Phase 1 only | US3, US4, US5, US7, US8, US9, US10, US11 |
| US7 (Legal/Terms) | Phase 1 only | US3, US4, US5, US6, US8, US9, US10, US11 |
| US8 (IA) | Phase 1 only | US3, US4, US5, US6, US7, US9, US10, US11 |
| US9 (Role Signup) | Phase 1 only | US3, US4, US5, US6, US7, US8, US10, US11 |
| US10 (Client Portal) | US9 (needs role signup) | US11 |
| US11 (Detective Portal) | US9 (needs role signup) | US10 |

### Within Each User Story

1. Configuration/setup tasks first
2. Implementation tasks second
3. Verification/test tasks last
4. All [P] marked tasks can run in parallel

### Parallel Opportunities

**Phase 2 (AWS)**:
```
T005 (dev bucket) || T006 (prod bucket) - parallel
T008 (dev notification) || T009 (prod notification) - parallel
```

**Phase 5-7 (US3, US4, US5)** can run entirely in parallel:
```
US3 Frontend Error Handling
US4 CI Test Coverage
US5 Permissions
```

**Within US3**:
```
T023 (toast in client) || T024 (useRetry hook) - parallel
```

**Within US4**:
```
T029 (backend threshold) || T030 (ai_worker threshold) - parallel
T032 (draft tests) || T033 (search tests) || T034 (qdrant tests) - parallel
```

**Within US5**:
```
T037 (cases audit) || T038 (evidence audit) || T039 (drafts audit) - parallel
```

---

## Parallel Example: US3 + US4 + US5

```bash
# These three user stories can run in parallel after Phase 1

# Developer A: US3 Frontend Error Handling
Task: "Install react-hot-toast: cd frontend && npm install react-hot-toast"
Task: "Add Toaster component to frontend/src/app/layout.tsx"

# Developer B: US4 CI Tests
Task: "Update backend coverage threshold to 70% in backend/pytest.ini"
Task: "Add unit tests for draft_service.py in backend/tests/unit/test_draft_service.py"

# Developer C: US5 Permissions
Task: "Audit /cases/* endpoints for permission checks in backend/app/api/cases.py"
Task: "Add audit_log write for ACCESS_DENIED in backend/app/services/audit_log_service.py"
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup (verification)
2. Complete Phase 2: Foundational (AWS infrastructure)
3. Complete Phase 3: US1 (AI Worker operational)
4. Complete Phase 4: US2 (RAG/Draft functional)
5. **STOP and VALIDATE**: Test full evidence upload → draft generation flow
6. Deploy to staging for demo

### Incremental Delivery (Recommended)

1. **Week 1**: Phase 1-3 (Setup → AWS → US1) → AI Worker operational
2. **Week 2**: Phase 4-6 (US2, US3, US4) in parallel → Core features + quality
3. **Week 3**: Phase 7-8 (US5, US6) → Security + deployment
4. **Week 4**: Phase 9 (Polish) → Production ready

### Single Developer Strategy

Execute in priority order:
1. T001-T010: Setup + AWS (2-3 hours)
2. T011-T015: US1 verification (1 hour)
3. T016-T020: US2 verification (1 hour)
4. T021-T028: US3 error handling (3-4 hours)
5. T029-T036: US4 CI tests (4-6 hours)
6. T037-T043: US5 permissions (3-4 hours)
7. T044-T050: US6 deployment (2-3 hours)
8. T051-T055: Polish (2 hours)

**Total estimated time**: 20-25 hours

---

## Phase 13: Code Quality - DraftService 리팩토링 (Priority: P2)

**Goal**: Decompose God Class DraftService (1186 lines) into focused, single-responsibility services

**Problem**: DraftService violates Single Responsibility Principle with 5+ concerns:
- RAG search orchestration
- Prompt building
- Document rendering (DOCX/PDF)
- Evidence context formatting
- Citation extraction

**Independent Test**: After refactoring, all existing draft-related tests must pass without modification

### Implementation for DraftService Decomposition

**⚠️ CRITICAL**: No functional changes - structure only. All existing tests must pass.

- [ ] T075 [P] [REFACTOR] Create `backend/app/services/rag_orchestrator.py` (~200 lines)
  - Extract: `_perform_rag_search()`, `_build_qdrant_filter()`, `_format_rag_context()`
  - Dependencies: Qdrant client, case_repository

- [ ] T076 [P] [REFACTOR] Create `backend/app/services/prompt_builder.py` (~150 lines)
  - Extract: `_build_draft_prompt()`, `_format_legal_context()`, `_format_evidence_context()`
  - Dependencies: None (pure functions)

- [ ] T077 [P] [REFACTOR] Create `backend/app/services/citation_extractor.py` (~100 lines)
  - Extract: `_extract_citations()`, citation parsing logic
  - Dependencies: None (pure functions)

- [ ] T078 [REFACTOR] Refactor DraftService to orchestrator pattern (~200 lines target)
  - Import and use: RAGOrchestrator, PromptBuilder, CitationExtractor
  - Keep: `generate_draft_preview()`, `export_draft()` as thin orchestrators
  - Remove: All extracted private methods
  - File: `backend/app/services/draft_service.py`

- [ ] T079 [REFACTOR] Update imports in `backend/app/api/drafts.py` if needed
  - Verify DraftService interface unchanged
  - No API contract changes allowed

- [ ] T080 [REFACTOR] Run existing tests: `pytest backend/tests/ -k draft`
  - All tests must pass without modification
  - If tests fail, fix refactoring (not tests)

- [ ] T081 [REFACTOR] Update `backend/app/services/__init__.py` with new exports

**Checkpoint**: DraftService < 300 lines, all tests pass, no API changes

### Refactoring Metrics

| Metric | Before | Target |
|--------|--------|--------|
| DraftService lines | 1,186 | < 300 |
| Methods in DraftService | 17 | < 6 |
| Imports in DraftService | 25 | < 10 |
| New services created | 0 | 3 |

---

## Notes

- Most code is already implemented (70-100% complete per user story)
- Focus is on configuration, verification, and polish
- AWS tasks (Phase 2) require appropriate IAM permissions
- CI tasks (US4) may require running tests locally first to identify gaps - **80% coverage required per Constitution**
- Commit after each task or logical group
- Create PR after each user story for review
- **Total Tasks**: 105 (T001-T105)
  - Core Tasks (T001-T055 + T019a): 56
  - NFR Tasks (T056-T059): 4 - Deferred to post-MVP (Phase 10)
  - US7 Legal/Terms (T060-T069): 10 - P2 priority
  - US8 IA Improvement (T070-T074): 5 - P3 priority
  - Phase 13 Refactoring (T075-T081): 7 - P2 priority, code quality
  - US9 Role Signup (T082-T087): 6 - P2 priority, role selection at signup
  - US10 Client Portal (T088-T095): 8 - P2 priority, client evidence upload & review
  - US11 Detective Portal (T096-T105): 10 - P2 priority, EXIF extraction & earnings
