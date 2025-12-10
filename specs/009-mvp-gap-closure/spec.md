# Feature Specification: MVP 구현 갭 해소 (Production Readiness)

**Feature Branch**: `009-mvp-gap-closure`
**Created**: 2025-12-09
**Status**: Draft
**Input**: User description: "MVP 구현 갭 해소 - 문서/설계 대비 실제 구현 갭을 좁히고 production-ready 상태로 만들기"

## Clarifications

### Session 2025-12-09

- Q: Draft 생성 후 편집 방식? → A: 초안작성에 필요한 웹 편집툴 연결 (Web-based editor integration required)
- Q: 지원 증거 파일 형식? → A: Images + Audio + Video + PDF + Text (jpg, png, mp3, wav, mp4, pdf, txt, csv)
- Q: 웹 편집툴 구현 방식? → A: Rich text editor (TipTap/Quill) embedded in frontend
- Q: 최대 증거 파일 크기? → A: 500MB (영상 녹화 파일 지원)
- Q: Observability 요구사항? → A: Standard (CloudWatch logs + Lambda metrics + API latency tracking)

### Session 2025-12-10

- Q: 저작권 표시? → A: 모든 페이지 푸터에 "© 2025 [회사명]. All Rights Reserved. 무단 활용 금지." 명시
- Q: 약관 업데이트? → A: 이용약관(ToS) 페이지 `/terms` 추가
- Q: 개인정보보호? → A: 개인정보처리방침 페이지 `/privacy` 추가 (PIPA 준수)
- Q: 회원가입 약관 동의? → A: 가입 시 ToS + Privacy 동의 체크박스 필수, 동의 이력 DB 저장
- Q: IA 개선? → A: 메인 네비게이션 1-depth 배치, 사건 상세에서 1클릭 접근, 일관된 뒤로가기 동작

### Session 2025-12-10 (Client/Detective Portal)

- Q: 회원가입 시 역할 선택 방식? → A: 단일 회원가입 페이지에 역할 선택 드롭다운 추가 (변호사/의뢰인/탐정)
- Q: 의뢰인 증거 업로드 권한? → A: 의뢰인이 직접 증거 업로드 가능, 변호사 검토 후 공식 증거로 채택
- Q: 탐정 현장 조사 기능? → A: 현장용 앱 아님, 업로드된 파일에서 EXIF 등 메타데이터 추출하여 표시
- Q: 역할별 케이스 접근 범위? → A: 자신이 관련된 케이스만 (의뢰인: 본인 케이스, 탐정: 배정된 케이스)
- Q: 회원가입 후 온보딩 플로우? → A: 역할별 대시보드로 직접 이동 (변호사→/lawyer, 의뢰인→/client, 탐정→/detective)

## 배경 (Background)

현재 LEH 프로젝트는 엔터프라이즈급 문서/설계가 완성되어 있으나, 실제 구현과의 갭이 존재:

- **AI Worker**: 코드/테스트 완성, S3 권한 미비로 배포 차단
- **Backend**: RAG 검색/Draft Preview API 미구현, 권한/감사로그 부분 적용
- **Frontend**: 버튼-API 스펙 불일치, 에러 처리 비일관성
- **Infra/CI**: IaC 미구성, 테스트 커버리지 CI에서 스킵

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Worker 실서비스 연동 (Priority: P1)

변호사가 증거 파일을 업로드하면, AI Worker가 자동으로 분석하여 타임라인/태그/요약을 생성한다.

**Why this priority**: AI Worker가 동작하지 않으면 핵심 기능(증거 분석, RAG 검색, Draft 생성)이 모두 불가능. 전체 시스템의 근간.

**Independent Test**: S3에 파일 업로드 후 DynamoDB/Qdrant에 분석 결과가 저장되는지 확인

**Acceptance Scenarios**:

1. **Given** S3 버킷 `leh-evidence-dev`가 존재하고, **When** 증거 파일이 `cases/{case_id}/raw/` 경로에 업로드되면, **Then** AI Worker Lambda가 트리거되어 5분 내 분석 완료
2. **Given** AI Worker가 분석 완료하면, **When** DynamoDB를 조회하면, **Then** 증거 메타데이터(요약, 840조 태그, 증거력 점수)가 저장됨
3. **Given** AI Worker가 분석 완료하면, **When** Qdrant를 조회하면, **Then** 임베딩 벡터가 `case_rag_{case_id}` 컬렉션에 저장됨

---

### User Story 2 - Backend RAG 검색 및 Draft 생성 (Priority: P1)

변호사가 사건 페이지에서 "AI 분석 요청" 버튼을 클릭하면, 관련 증거를 검색하고 초안을 생성한다.

**Why this priority**: 사용자가 직접 경험하는 핵심 AI 기능. 이 기능이 없으면 "AI 파라리걸" 가치 제안이 무효화됨.

**Independent Test**: 사건 상세 페이지에서 Draft 생성 요청 시 실제 초안이 반환되는지 확인

**Acceptance Scenarios**:

1. **Given** 사건에 3개 이상의 분석된 증거가 있을 때, **When** 변호사가 RAG 검색을 실행하면, **Then** 관련도 순으로 증거 목록이 반환됨
2. **Given** 사건 증거가 분석 완료된 상태에서, **When** Draft Preview를 요청하면, **Then** 증거 인용이 포함된 초안이 30초 내 반환됨
3. **Given** Draft가 생성되면, **Then** 각 문장에 출처 증거 ID가 명시됨

---

### User Story 3 - Frontend 에러 처리 통일 (Priority: P2)

사용자가 어떤 기능을 사용하든, 오류 발생 시 일관된 피드백을 받고 다음 행동을 알 수 있다.

**Why this priority**: 현재 에러 처리가 산발적이어서 사용자 경험 저하. P1 기능이 완성되어도 에러 시 UX가 나쁘면 서비스 신뢰도 하락.

**Independent Test**: 의도적으로 네트워크 오류/서버 오류 발생시키고 일관된 에러 메시지 확인

**Acceptance Scenarios**:

1. **Given** 사용자가 로그인한 상태에서, **When** 세션이 만료되면(401), **Then** 자동으로 로그인 페이지로 이동하고 "세션이 만료되었습니다" 메시지 표시
2. **Given** API 호출 중 네트워크 오류 발생 시, **When** 화면에 에러 표시, **Then** "다시 시도" 버튼과 함께 사용자 친화적 메시지 표시
3. **Given** 버튼 클릭 후 API 호출 중, **When** 로딩 상태일 때, **Then** 버튼이 비활성화되고 로딩 인디케이터 표시

---

### User Story 4 - CI 테스트 커버리지 정상화 (Priority: P2)

개발자가 PR을 올리면, 실제 테스트가 실행되어 코드 품질이 검증된다.

**Why this priority**: 현재 CI에서 테스트가 스킵되어 "테스트 통과"가 무의미. 품질 게이트 역할을 하지 못함.

**Independent Test**: PR 생성 시 CI에서 테스트 커버리지 65% 이상 달성 확인

**Acceptance Scenarios**:

1. **Given** ai_worker 코드 변경 PR, **When** CI 실행 시, **Then** 유닛 테스트 300개 이상이 실제 실행됨 (스킵 아님)
2. **Given** backend 코드 변경 PR, **When** CI 실행 시, **Then** 테스트 커버리지 65% 이상 달성
3. **Given** frontend 코드 변경 PR, **When** CI 실행 시, **Then** lint + 유닛 테스트 통과

---

### User Story 5 - 사건별 권한 제어 (Priority: P2)

사건에 소속되지 않은 사용자는 해당 사건의 정보에 접근할 수 없다.

**Why this priority**: 법률 정보의 민감성상 권한 제어는 필수. P1보다 낮지만 배포 전 반드시 필요.

**Independent Test**: 다른 사건 소속 사용자가 해당 사건 API 호출 시 403 반환 확인

**Acceptance Scenarios**:

1. **Given** 사용자 A가 사건 1의 멤버일 때, **When** 사건 2의 증거를 조회하면, **Then** 403 Forbidden 반환
2. **Given** case_members 테이블에 사용자-사건 매핑이 있을 때, **When** 해당 사건 API 호출 시, **Then** 정상 응답
3. **Given** 모든 사건 관련 API 호출 시, **When** 권한이 없으면, **Then** audit_logs 테이블에 접근 시도 기록됨

---

### User Story 6 - 기본 배포 파이프라인 (Priority: P3)

코드가 main 브랜치에 머지되면, 자동으로 production 환경에 배포된다.

**Why this priority**: MVP 기능이 완성되어야 배포 의미가 있음. P1/P2 완료 후 필요.

**Independent Test**: main 브랜치 머지 후 CloudFront URL에서 신규 기능 확인

**Acceptance Scenarios**:

1. **Given** dev 브랜치에 코드 머지, **When** CI 통과 후, **Then** staging 환경에 자동 배포
2. **Given** main 브랜치에 코드 머지, **When** CI 통과 후, **Then** production 환경에 배포 (수동 승인 후)
3. **Given** 배포 실패 시, **When** 롤백 필요하면, **Then** 이전 버전으로 5분 내 복구 가능

---

### User Story 7 - 법적 고지 및 약관 동의 (Priority: P2)

사용자가 서비스를 이용하기 전에 저작권, 약관, 개인정보처리방침에 동의하고, 해당 내용을 명확히 확인할 수 있다.

**Why this priority**: 법적 보호와 규정 준수(PIPA)가 서비스 운영의 전제조건. 배포 전 반드시 필요.

**Independent Test**: 회원가입 시 약관 동의 체크박스 확인, 푸터에서 약관/개인정보처리방침 링크 접근 가능 확인

**Acceptance Scenarios**:

1. **Given** 신규 사용자가 회원가입 페이지에 접근, **When** 가입 양식을 작성할 때, **Then** 이용약관과 개인정보처리방침 동의 체크박스가 필수로 표시됨
2. **Given** 사용자가 동의 체크박스를 선택하지 않고, **When** 가입 버튼을 클릭하면, **Then** "약관에 동의해주세요" 에러 메시지 표시
3. **Given** 로그인한 사용자가 푸터를 확인할 때, **When** 저작권 표시가 있으면, **Then** "© 2025 [회사명]. All Rights Reserved. 무단 활용 금지." 문구 표시
4. **Given** 사용자가 약관 또는 개인정보처리방침 링크를 클릭하면, **When** 해당 페이지로 이동, **Then** 전문이 표시됨

---

### User Story 8 - 정보 구조(IA) 개선 (Priority: P3)

사용자가 서비스 내에서 원하는 기능에 쉽게 접근할 수 있도록 화면 간 연결 관계가 명확하다.

**Why this priority**: UX 개선 사항으로 핵심 기능 완성 후 진행. 사용성 향상에 기여.

**Independent Test**: 메인 네비게이션에서 모든 주요 기능에 3클릭 이내 접근 가능 확인

**Acceptance Scenarios**:

1. **Given** 로그인한 변호사가 대시보드에 접근, **When** 네비게이션 메뉴를 확인하면, **Then** 사건목록/증거업로드/초안생성/설정이 1-depth에 표시됨
2. **Given** 사용자가 사건 상세 페이지에 있을 때, **When** 관련 기능(증거, 당사자, 초안)을 찾으면, **Then** 탭 또는 사이드바로 1클릭 접근 가능
3. **Given** 사용자가 어떤 페이지에서든, **When** 뒤로가기/홈 버튼을 클릭하면, **Then** 예상한 페이지로 이동 (일관된 네비게이션)

---

### User Story 9 - 회원가입 역할 선택 (Priority: P2)

사용자가 회원가입 시 자신의 역할(변호사/의뢰인/탐정)을 선택하여 해당 역할에 맞는 포털로 이동한다.

**Why this priority**: 역할별 포털이 이미 구현되어 있으나 회원가입에서 역할 선택이 불가능. 의뢰인/탐정 사용자 유입에 필수.

**Independent Test**: 회원가입 페이지에서 역할 선택 후 해당 역할 대시보드로 이동 확인

**Acceptance Scenarios**:

1. **Given** 회원가입 페이지에 접근, **When** 양식을 확인하면, **Then** 역할 선택 드롭다운(변호사/의뢰인/탐정)이 표시됨
2. **Given** 사용자가 "의뢰인" 역할을 선택하고 가입 완료, **When** 로그인하면, **Then** `/client/dashboard`로 리다이렉트됨
3. **Given** 사용자가 "탐정" 역할을 선택하고 가입 완료, **When** 로그인하면, **Then** `/detective/dashboard`로 리다이렉트됨
4. **Given** 역할을 선택하지 않고 가입 시도, **When** 제출하면, **Then** "역할을 선택해주세요" 에러 표시

---

### User Story 10 - 의뢰인(Client) 포털 기능 (Priority: P2)

의뢰인이 자신의 케이스 상태를 확인하고, 증거를 업로드하며, 변호사와 소통할 수 있다.

**Why this priority**: 의뢰인 참여가 케이스 진행 효율성 향상에 기여. 변호사 업무 부담 감소.

**Independent Test**: 의뢰인 계정으로 로그인 후 케이스 조회, 증거 업로드, 메시지 전송 가능 확인

**Acceptance Scenarios**:

1. **Given** 의뢰인이 `/client/dashboard`에 접근, **When** 자신의 케이스를 조회하면, **Then** 본인이 관련된 케이스만 목록에 표시됨
2. **Given** 의뢰인이 케이스 상세 페이지에서, **When** 증거 업로드를 시도하면, **Then** S3에 파일이 업로드되고 "검토 대기" 상태로 표시됨
3. **Given** 의뢰인이 업로드한 증거가 있을 때, **When** 변호사가 검토/승인하면, **Then** 해당 증거가 "공식 증거"로 상태 변경됨
4. **Given** 의뢰인이 메시지 페이지에서, **When** 변호사에게 메시지를 전송하면, **Then** 변호사의 메시지함에 표시됨
5. **Given** 의뢰인이 다른 케이스(본인 미관련)에 접근 시도, **When** API 호출하면, **Then** 403 Forbidden 반환

---

### User Story 11 - 탐정(Detective) 포털 기능 (Priority: P2)

탐정이 배정된 케이스의 조사 업무를 수행하고, 증거를 업로드하며, 수익을 확인할 수 있다.

**Why this priority**: 탐정 역할의 증거 수집이 케이스 진행에 필수. 분업 체계 완성.

**Independent Test**: 탐정 계정으로 로그인 후 배정 케이스 조회, 증거 업로드(메타데이터 자동 추출), 수익 확인

**Acceptance Scenarios**:

1. **Given** 탐정이 `/detective/dashboard`에 접근, **When** 케이스 목록을 조회하면, **Then** 본인에게 배정된 케이스만 표시됨
2. **Given** 탐정이 증거 파일(사진)을 업로드할 때, **When** 파일에 EXIF 데이터가 있으면, **Then** 위치/시간 메타데이터가 자동으로 추출되어 표시됨
3. **Given** 탐정이 `/detective/earnings`에 접근, **When** 정산 내역을 조회하면, **Then** 케이스별 수익과 총 정산 금액이 표시됨
4. **Given** 탐정이 미배정 케이스에 접근 시도, **When** API 호출하면, **Then** 403 Forbidden 반환

---

### Edge Cases

- AI Worker Lambda가 타임아웃(15분 초과) 발생 시 어떻게 처리?
  → DynamoDB에 `status: failed` 기록, 사용자에게 "분석 실패" 알림
- Qdrant 연결 실패 시 증거 업로드가 실패해야 하나?
  → 메타데이터는 DynamoDB에 저장, 벡터 저장만 재시도 큐에 추가
- 사건 소유자가 삭제된 경우 다른 멤버가 사건에 접근 가능한가?
  → 사건에 최소 1명의 OWNER 역할 필수, 없으면 관리자 개입 필요

## Requirements *(mandatory)*

### Functional Requirements

**AI Worker (US1)**
- **FR-001**: S3 버킷 `leh-evidence-dev`, `leh-evidence-prod` 생성 및 Lambda 실행 역할에 권한 부여
- **FR-001a**: 지원 파일 형식: Images (jpg, png), Audio (mp3, wav), Video (mp4), PDF, Text (txt, csv)
- **FR-001b**: 최대 파일 크기 500MB (S3 multipart upload, 대용량 영상 지원)
- **FR-002**: AI Worker Lambda가 S3 `ObjectCreated` 이벤트에 의해 자동 트리거됨
- **FR-003**: 분석 결과가 DynamoDB `leh_evidence` 테이블에 저장됨
- **FR-004**: 임베딩 벡터가 Qdrant `case_rag_{case_id}` 컬렉션에 저장됨

**Backend RAG/Draft (US2)**
- **FR-005**: `GET /search?q={query}&case_id={id}` API가 Qdrant에서 유사 증거를 검색하여 반환
- **FR-006**: `POST /cases/{id}/draft-preview` API가 GPT-4o를 사용하여 초안 생성
- **FR-007**: Draft 응답에 각 문장별 출처 증거 ID가 포함됨
- **FR-007a**: 생성된 Draft를 TipTap/Quill 기반 Rich Text Editor에서 수정 가능

**Frontend 에러 처리 (US3)**
- **FR-008**: 401 응답 시 자동으로 로그인 페이지 리다이렉트 및 메시지 표시
- **FR-009**: 네트워크 오류 시 토스트/배너로 사용자 친화적 메시지 표시
- **FR-010**: API 호출 중 버튼 비활성화 및 로딩 상태 표시

**CI 테스트 (US4)**
- **FR-011**: `ai_worker/tests/conftest.py`에서 환경변수 미설정 시 전체 스킵 대신 특정 통합 테스트만 스킵
- **FR-012**: CI에서 ai_worker 유닛 테스트 최소 300개 실행
- **FR-013**: CI에서 backend 테스트 커버리지 80% 이상 검증 (Constitution requirement)

**권한 제어 (US5)**
- **FR-014**: 모든 `/cases/*`, `/evidence/*`, `/draft/*` API에 사건 멤버 권한 검증 미들웨어 적용
- **FR-015**: 권한 없는 접근 시 403 반환 및 audit_logs 테이블에 기록
- **FR-016**: audit_logs 테이블에 사용자 ID, 액션, 타임스탬프, IP 기록

**배포 파이프라인 (US6)**
- **FR-017**: GitHub Actions에서 dev 머지 시 staging 자동 배포
- **FR-018**: GitHub Actions에서 main 머지 시 production 배포 (수동 승인)
- **FR-019**: 배포 실패 시 이전 버전으로 롤백 가능

**법적 고지 및 약관 (US7)**
- **FR-020**: 모든 페이지 푸터에 저작권 표시: "© 2025 [회사명]. All Rights Reserved. 무단 활용 금지."
- **FR-021**: 회원가입 시 이용약관(ToS) 동의 체크박스 필수
- **FR-022**: 회원가입 시 개인정보처리방침(Privacy Policy) 동의 체크박스 필수
- **FR-023**: `/terms` 페이지에 이용약관 전문 표시
- **FR-024**: `/privacy` 페이지에 개인정보처리방침 전문 표시 (PIPA 준수)
- **FR-025**: 사용자 동의 이력이 `user_agreements` 테이블에 기록됨 (user_id, agreement_type, agreed_at, version)

**정보 구조 개선 (US8)**
- **FR-026**: 메인 네비게이션에 주요 기능 1-depth 배치 (사건목록, 증거업로드, 초안생성, 설정)
- **FR-027**: 사건 상세 페이지에서 관련 기능(증거, 당사자, 초안)에 1클릭 접근 가능
- **FR-028**: 모든 페이지에서 일관된 뒤로가기/홈 버튼 동작 보장

**회원가입 역할 선택 (US9)**
- **FR-029**: 회원가입 페이지에 역할 선택 드롭다운 추가 (변호사/의뢰인/탐정)
- **FR-030**: 선택된 역할이 백엔드 `POST /auth/signup` API에 `role` 파라미터로 전달됨
- **FR-031**: 회원가입/로그인 후 역할에 따라 적절한 대시보드로 리다이렉트 (lawyer→/lawyer, client→/client, detective→/detective)
- **FR-032**: 역할 미선택 시 회원가입 버튼 비활성화 및 에러 메시지 표시

**의뢰인 포털 (US10)**
- **FR-033**: 의뢰인은 자신이 `case_members`에 등록된 케이스만 조회 가능
- **FR-034**: 의뢰인이 증거 업로드 시 `evidence.status = 'pending_review'`로 저장
- **FR-035**: 변호사가 의뢰인 업로드 증거를 검토/승인하면 `evidence.status = 'approved'`로 변경
- **FR-036**: 의뢰인 포털 메시지 기능: 담당 변호사에게 메시지 전송 가능

**탐정 포털 (US11)**
- **FR-037**: 탐정은 자신이 `case_members`에 배정된 케이스만 조회 가능
- **FR-038**: 탐정이 업로드한 이미지에서 EXIF 메타데이터(GPS 좌표, 촬영 시간) 자동 추출
- **FR-039**: `/detective/earnings` 페이지에서 케이스별 수익 및 총 정산 금액 표시
- **FR-040**: 탐정 정산 데이터는 `detective_earnings` 테이블에서 조회

### Key Entities

- **Evidence**: 증거 파일 메타데이터 (case_id, type, timestamp, ai_summary, labels, qdrant_id, status: pending_review/approved/rejected, uploaded_by)
- **AuditLog**: 감사 로그 (user_id, action, resource_type, resource_id, ip_address, created_at)
- **CaseMember**: 사건-사용자 권한 매핑 (case_id, user_id, role: OWNER/MEMBER/VIEWER)
- **UserAgreement**: 사용자 약관 동의 이력 (user_id, agreement_type: ToS/Privacy, agreed_at, version)
- **DetectiveEarnings**: 탐정 수익 정산 (detective_id, case_id, amount, status: pending/paid, created_at, paid_at)

### Non-Functional Requirements

**Observability (NFR-001~003)** - *Deferred to P3 for MVP*
- **NFR-001**: 모든 Lambda 함수에서 CloudWatch Logs로 구조화된 로그 출력 (JSON format: timestamp, level, message, trace_id)
- **NFR-002**: Lambda 실행 시간, 메모리 사용량, 에러율 CloudWatch Metrics 수집
- **NFR-003**: Backend API 응답 시간 로깅 (p50, p95, p99 latency tracking)

> **Note**: NFR-001~003 are deferred to post-MVP (Phase 10). Basic CloudWatch logging is already enabled by default.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 증거 파일 업로드 후 5분 이내에 AI 분석 완료 및 결과 조회 가능
- **SC-002**: RAG 검색 결과가 2초 이내에 반환됨
- **SC-003**: Draft Preview가 30초 이내에 생성됨
- **SC-004**: CI에서 ai_worker 테스트 300개 이상 실행 (스킵 제외)
- **SC-005**: Backend 테스트 커버리지 80% 이상 유지 (Constitution requirement)
- **SC-006**: 권한 없는 API 접근 시 100% 403 반환
- **SC-007**: dev→staging 배포가 CI 통과 후 10분 이내 완료
- **SC-008**: 모든 API 에러 시 사용자 친화적 메시지 표시율 100%
- **SC-009**: 회원가입 시 약관 동의 없이 가입 불가 (100% 검증)
- **SC-010**: 모든 페이지 푸터에 저작권 표시 확인
- **SC-011**: 주요 기능에 메인 네비게이션에서 3클릭 이내 접근 가능
- **SC-012**: 회원가입 시 역할 선택 필수 (100% 검증)
- **SC-013**: 역할별 로그인 후 올바른 대시보드로 리다이렉트 (100% 검증)
- **SC-014**: 의뢰인/탐정은 미관련 케이스 접근 시 100% 403 반환
- **SC-015**: 의뢰인 업로드 증거는 변호사 승인 전까지 "검토 대기" 상태 유지
- **SC-016**: 탐정 업로드 이미지에서 EXIF 메타데이터 추출 성공률 90% 이상

## Assumptions

- S3 버킷 생성 및 IAM 역할 설정은 AWS 콘솔 또는 CLI로 수동 진행 (Terraform 미사용)
- Qdrant Cloud 인스턴스는 이미 프로비저닝됨
- OpenAI API 키는 환경변수로 설정됨
- 현재 테스트 코드의 대부분은 유효하며, conftest.py 수정만으로 CI 실행 가능
- GitHub Actions 워크플로우 파일은 이미 존재하며 수정만 필요

## Out of Scope

- Terraform/IaC 완전 자동화 (수동 AWS 설정으로 대체)
- 실시간 알림 시스템 (WebSocket)
- 다국어 지원
- 모바일 앱
- 고급 분석 대시보드
