# 01. 프로젝트 구조

> **목표**: LEH 프로젝트의 폴더 구조를 이해하고, 필요한 코드를 어디서 찾아야 하는지 파악합니다.

---

## 전체 폴더 구조

```
leh/                              # 프로젝트 루트
│
├── frontend/                     # 🖥️ 프론트엔드 (Next.js)
│   ├── src/
│   │   ├── app/                 # 페이지 라우팅 (App Router)
│   │   ├── components/          # React 컴포넌트
│   │   ├── hooks/               # 커스텀 React Hooks
│   │   ├── lib/                 # 유틸리티, API 클라이언트
│   │   └── types/               # TypeScript 타입 정의
│   ├── package.json
│   └── next.config.js
│
├── backend/                      # ⚙️ 백엔드 (FastAPI)
│   ├── app/
│   │   ├── api/                 # API 라우터 (엔드포인트)
│   │   ├── services/            # 비즈니스 로직
│   │   ├── repositories/        # 데이터 접근 계층
│   │   ├── db/                  # 데이터베이스 모델, 스키마
│   │   ├── core/                # 설정, 보안, 의존성
│   │   ├── middleware/          # 미들웨어 (에러, 로깅)
│   │   └── utils/               # AWS 연동 유틸리티
│   ├── alembic/                 # DB 마이그레이션
│   ├── tests/                   # 테스트 코드
│   └── requirements.txt
│
├── ai_worker/                    # 🤖 AI 워커 (Lambda)
│   ├── handler.py               # Lambda 진입점
│   ├── src/
│   │   ├── parsers/             # 파일 타입별 파서
│   │   ├── analysis/            # AI 분석 엔진
│   │   ├── storage/             # DynamoDB, Qdrant 저장
│   │   └── utils/               # 유틸리티
│   └── tests/
│
├── infrastructure/               # 🏗️ 인프라 설정
│   └── terraform/               # IaC (Infrastructure as Code)
│
├── docs/                         # 📚 문서
│   ├── specs/                   # 설계 명세서
│   ├── guides/                  # 개발 가이드
│   └── architecture/            # 아키텍처 문서 (지금 읽고 있는 곳!)
│
├── .github/
│   └── workflows/               # 🚀 CI/CD 파이프라인
│       ├── ci.yml               # 테스트 자동화
│       └── deploy_paralegal.yml # 배포 자동화
│
├── .env                         # 환경변수 (비밀! .gitignore됨)
├── .env.example                 # 환경변수 템플릿
├── docker-compose.yml           # 로컬 개발 환경
├── Makefile                     # 개발 편의 명령어
└── CLAUDE.md                    # 프로젝트 규칙 (필독!)
```

---

## 각 폴더 상세 설명

### 1. `frontend/` - 프론트엔드

사용자가 보는 화면을 담당합니다.

```
frontend/src/
├── app/                         # Next.js App Router
│   ├── page.tsx                # 메인 페이지 (/)
│   ├── layout.tsx              # 공통 레이아웃
│   ├── lawyer/                 # 변호사 포털
│   │   ├── cases/             # 케이스 관리
│   │   ├── clients/           # 의뢰인 관리
│   │   └── calendar/          # 일정 관리
│   ├── client/                 # 의뢰인 포털
│   ├── staff/                  # 스태프 포털
│   └── admin/                  # 관리자 포털
│
├── components/                  # 재사용 가능한 컴포넌트
│   ├── case/                   # 케이스 관련 컴포넌트
│   ├── evidence/               # 증거 관련 컴포넌트
│   ├── draft/                  # 초안 관련 컴포넌트
│   ├── party/                  # 당사자 그래프 컴포넌트
│   └── ui/                     # 공통 UI 컴포넌트
│
├── hooks/                       # 커스텀 Hooks
│   ├── useAuth.ts             # 인증 상태 관리
│   ├── useCase.ts             # 케이스 데이터 관리
│   └── useEvidence.ts         # 증거 데이터 관리
│
├── lib/                         # 유틸리티
│   └── api/                    # API 클라이언트
│       ├── auth.ts            # 인증 API
│       ├── cases.ts           # 케이스 API
│       └── evidence.ts        # 증거 API
│
└── types/                       # TypeScript 타입
    ├── case.ts                # Case 타입 정의
    ├── user.ts                # User 타입 정의
    └── evidence.ts            # Evidence 타입 정의
```

**핵심 파일**:
- `app/page.tsx` - 메인 페이지
- `components/ui/` - 버튼, 모달 등 공통 컴포넌트
- `lib/api/` - 백엔드 API 호출 함수

---

### 2. `backend/` - 백엔드

API 서버를 담당합니다. **Clean Architecture** 패턴을 따릅니다.

```
backend/app/
├── api/                         # 📡 라우터 (HTTP 요청 처리)
│   ├── auth.py                 # POST /auth/login, /register
│   ├── cases.py                # CRUD /cases
│   ├── evidence.py             # CRUD /evidence
│   ├── drafts.py               # POST /drafts/preview
│   └── ...                     # 30+ 라우터 파일
│
├── services/                    # 💼 서비스 (비즈니스 로직)
│   ├── auth_service.py         # 로그인, 회원가입 로직
│   ├── case_service.py         # 케이스 생성, 조회 로직
│   ├── evidence_service.py     # 증거 업로드, 분석 로직
│   └── draft_service.py        # 초안 생성 로직
│
├── repositories/                # 🗄️ 리포지토리 (데이터 접근)
│   ├── user_repository.py      # User 테이블 CRUD
│   ├── case_repository.py      # Case 테이블 CRUD
│   └── evidence_repository.py  # Evidence 테이블 CRUD
│
├── db/                          # 💾 데이터베이스
│   ├── models/                 # SQLAlchemy 모델 (테이블 정의)
│   │   ├── auth.py            # User, InviteToken
│   │   ├── case.py            # Case, CaseMember
│   │   └── evidence.py        # Evidence
│   ├── schemas/                # Pydantic 스키마 (입출력 검증)
│   └── session.py              # DB 연결 관리
│
├── core/                        # ⚙️ 핵심 설정
│   ├── config.py               # 환경변수 로드
│   ├── dependencies.py         # 의존성 주입 (DI)
│   └── security.py             # JWT 토큰 생성/검증
│
├── middleware/                  # 🔧 미들웨어
│   ├── error_handler.py        # 에러 처리
│   └── audit_log.py            # 감사 로그
│
└── utils/                       # 🛠️ 유틸리티 (AWS 연동)
    ├── s3.py                   # S3 Presigned URL
    ├── dynamo.py               # DynamoDB 연동
    ├── qdrant.py               # Qdrant 벡터 검색
    └── openai_client.py        # OpenAI API 연동
```

**핵심 파일**:
- `app/main.py` - FastAPI 앱 진입점
- `app/core/config.py` - 환경변수 설정
- `app/core/dependencies.py` - 인증, DB 세션 주입

**코드 흐름**: `api/` → `services/` → `repositories/` → `db/`

---

### 3. `ai_worker/` - AI 워커

증거 파일을 분석하는 AI 파이프라인입니다.

```
ai_worker/
├── handler.py                   # 🚪 Lambda 진입점
│                                # S3 이벤트를 받아 처리
│
└── src/
    ├── parsers/                 # 📄 파일 타입별 파서
    │   ├── text.py             # 텍스트 파싱 (카카오톡 대화)
    │   ├── image_vision.py     # 이미지 분석 (GPT-4o Vision)
    │   ├── audio_parser.py     # 오디오 → 텍스트 (Whisper)
    │   ├── video_parser.py     # 비디오 → 오디오 → 텍스트
    │   └── pdf_parser.py       # PDF 텍스트 추출 + OCR
    │
    ├── analysis/                # 🧠 분석 엔진
    │   ├── summarizer.py       # 요약 생성
    │   ├── article_840_tagger.py  # 민법 840조 라벨링
    │   └── person_extractor.py # 인물 추출
    │
    └── storage/                 # 💾 저장
        ├── metadata_store.py   # DynamoDB 저장
        └── vector_store.py     # Qdrant 임베딩 저장
```

**핵심 파일**:
- `handler.py` - Lambda가 실행하는 함수
- `src/parsers/` - 각 파일 타입별 처리 로직

**트리거 방식**: S3에 파일이 업로드되면 자동으로 Lambda가 실행됩니다.

---

### 4. `.github/workflows/` - CI/CD

코드 변경 시 자동으로 테스트하고 배포합니다.

```
.github/workflows/
├── ci.yml                       # 🧪 CI (Continuous Integration)
│                                # - ESLint, Ruff 린팅
│                                # - pytest, Jest 테스트
│                                # - 커버리지 체크
│
└── deploy_paralegal.yml         # 🚀 CD (Continuous Deployment)
                                 # - Backend → ECR → Lambda
                                 # - AI Worker → ECR → Lambda
                                 # - Frontend → S3 → CloudFront
```

**핵심 파일**:
- `ci.yml` - PR마다 테스트 자동 실행
- `deploy_paralegal.yml` - main/dev 브랜치 푸시 시 자동 배포

---

## 파일을 찾을 때 참고하세요

### "새 API 엔드포인트를 만들고 싶어요"
→ `backend/app/api/` 에 라우터 파일 추가

### "비즈니스 로직을 수정하고 싶어요"
→ `backend/app/services/` 에서 해당 서비스 파일 수정

### "DB 테이블을 추가하고 싶어요"
→ `backend/app/db/models/` 에 모델 추가 후 Alembic 마이그레이션

### "새 React 컴포넌트를 만들고 싶어요"
→ `frontend/src/components/` 에 컴포넌트 추가

### "새 페이지를 만들고 싶어요"
→ `frontend/src/app/` 에 폴더/page.tsx 추가

### "AI 분석 로직을 수정하고 싶어요"
→ `ai_worker/src/parsers/` 또는 `ai_worker/src/analysis/` 수정

### "환경변수를 추가하고 싶어요"
→ `.env.example` 에 템플릿 추가, `.env` 에 실제 값 설정

---

## 환경변수 파일 (.env)

프로젝트 루트의 `.env` 파일이 모든 서비스에서 공유됩니다.

```bash
# 각 서비스 폴더의 .env는 루트 .env의 심볼릭 링크입니다
backend/.env    → ../.env (심볼릭 링크)
ai_worker/.env  → ../.env (심볼릭 링크)
frontend/.env   → ../.env (심볼릭 링크)
```

**주요 환경변수**:

```bash
# AWS
AWS_REGION=ap-northeast-2
S3_EVIDENCE_BUCKET=leh-evidence-prod

# Database
DATABASE_URL=postgresql://user:pass@host:5432/leh_db

# JWT (로그인 토큰)
JWT_SECRET=your-secret-key-min-32-chars

# OpenAI
OPENAI_API_KEY=sk-...

# Qdrant (벡터 검색)
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

---

## 핵심 파일 Quick Reference

| 목적 | 파일 경로 |
|------|----------|
| 프로젝트 규칙 | `CLAUDE.md` |
| 백엔드 진입점 | `backend/app/main.py` |
| 환경변수 설정 | `backend/app/core/config.py` |
| 인증 처리 | `backend/app/core/dependencies.py` |
| AI Worker 진입점 | `ai_worker/handler.py` |
| 프론트엔드 레이아웃 | `frontend/src/app/layout.tsx` |
| CI 설정 | `.github/workflows/ci.yml` |
| 배포 설정 | `.github/workflows/deploy_paralegal.yml` |

---

**다음 문서**: [02. 3-Tier 아키텍처](02-THREE_TIER_ARCHITECTURE.md) - Frontend, Backend, AI Worker가 어떻게 협력하는지 알아봅니다.
