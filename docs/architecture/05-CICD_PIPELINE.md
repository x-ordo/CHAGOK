# 05. CI/CD 파이프라인

> **목표**: 코드가 어떻게 자동으로 테스트되고 배포되는지 이해합니다.

---

## CI/CD란?

### CI (Continuous Integration, 지속적 통합)

코드 변경이 있을 때마다 자동으로 **테스트**하는 것입니다.

```
개발자가 코드 푸시
      │
      ▼
  자동 테스트 실행
      │
      ├── 성공 ✅ → 코드 병합 가능
      │
      └── 실패 ❌ → 코드 수정 필요
```

### CD (Continuous Deployment, 지속적 배포)

테스트가 통과하면 자동으로 **배포**하는 것입니다.

```
main 브랜치에 병합
      │
      ▼
  자동 배포 실행
      │
      ▼
  프로덕션 서버 업데이트
```

---

## CHAGOK의 CI/CD 구조

### 파일 위치

```
.github/workflows/
├── ci.yml                  # CI: 테스트 자동화
└── deploy_paralegal.yml    # CD: 배포 자동화
```

### 브랜치 전략

```
main (프로덕션)
 ↑
 │ PR (Pull Request)
 │
dev (스테이징)
 ↑
 │ PR
 │
feat/*, p-work, 011-*, 012-* (작업 브랜치)
```

| 브랜치 | 용도 | 배포 환경 |
|--------|------|----------|
| `main` | 프로덕션 코드 | Production (실 서비스) |
| `dev` | 개발 코드 | Staging (테스트 환경) |
| `feat/*` | 기능 개발 | 배포 안 함 |

**규칙**:
- `main`, `dev` 브랜치에 직접 푸시 금지!
- 항상 PR (Pull Request)을 통해 병합

---

## CI 파이프라인 (ci.yml)

### 언제 실행되나요?

```yaml
on:
  push:
    branches: [main, dev]   # main, dev에 푸시될 때
  pull_request:
    branches: [main, dev]   # main, dev로 PR 생성될 때
```

### 전체 흐름

```mermaid
flowchart TD
    A[코드 푸시/PR] --> B{Guard}
    B -->|통과| C[Frontend 테스트]
    B -->|통과| D[Backend 테스트]
    B -->|통과| E[AI Worker 테스트]
    B -->|실패| X[❌ 중단]

    C -->|성공| F[PR 코멘트]
    D -->|성공| F
    E -->|성공| F

    C -->|실패| X
    D -->|실패| X
    E -->|실패| X

    F --> G[✅ 병합 가능]
```

### 각 단계 상세

#### 1. Guard (사전 검사)

```yaml
guard:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Check for merge conflict markers
      run: |
        # 머지 충돌 마커 확인 (7개의 < 또는 > 문자열 검출)
        if grep -rn "^<\{7\}" --include="*.py" --include="*.ts" .; then
          echo "❌ Merge conflict markers found!"
          exit 1
        fi
```

**역할**: 머지 충돌 마커 (7개의 `<` 또는 `>` 문자)가 있으면 즉시 실패

#### 2. Frontend 테스트

```yaml
frontend:
  runs-on: ubuntu-latest
  timeout-minutes: 15  # 15분 제한
  defaults:
    run:
      working-directory: frontend

  steps:
    - uses: actions/checkout@v4

    # Node.js 설치
    - uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json

    # 의존성 설치
    - run: npm ci

    # 린팅 (코드 스타일 검사)
    - run: npm run lint

    # 테스트 실행
    - run: npm test -- --coverage

    # 빌드 확인
    - run: npm run build
```

**검사 항목**:
- ESLint 린팅 통과
- Jest 테스트 통과
- Next.js 빌드 성공

#### 3. Backend 테스트

```yaml
backend:
  runs-on: ubuntu-latest
  timeout-minutes: 10

  services:
    # 테스트용 PostgreSQL 컨테이너
    postgres:
      image: postgres:15
      env:
        POSTGRES_USER: test
        POSTGRES_PASSWORD: test
        POSTGRES_DB: test_db
      ports:
        - 5432:5432

  steps:
    - uses: actions/checkout@v4

    # Python 설치
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    # 의존성 설치
    - run: pip install -r requirements.txt
      working-directory: backend

    # 린팅 (Ruff)
    - run: ruff check .
      working-directory: backend

    # 테스트 실행
    - run: pytest --cov=app --cov-report=xml
      working-directory: backend
      env:
        DATABASE_URL: postgresql://test:test@localhost:5432/test_db
```

**검사 항목**:
- Ruff 린팅 통과
- pytest 테스트 통과
- 커버리지 목표: 80%

#### 4. AI Worker 테스트

```yaml
ai_worker:
  runs-on: ubuntu-latest
  timeout-minutes: 10

  steps:
    - uses: actions/checkout@v4

    # 시스템 의존성 설치
    - run: |
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr ffmpeg

    # Python 설치
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    # 의존성 설치
    - run: pip install -r requirements.txt
      working-directory: ai_worker

    # 테스트 실행
    - run: pytest --cov=src --cov-fail-under=80
      working-directory: ai_worker
```

**검사 항목**:
- Tesseract OCR, FFmpeg 필요 (이미지/비디오 처리용)
- pytest 테스트 통과
- 커버리지 최소 80%

---

## CD 파이프라인 (deploy_paralegal.yml)

### 언제 실행되나요?

```yaml
on:
  push:
    branches: [main, dev, 011-*, 012-*]  # 이 브랜치에 푸시될 때
  workflow_dispatch:                       # 수동 실행도 가능
    inputs:
      environment:
        description: 'Deployment environment'
        default: 'staging'
        type: choice
        options:
          - production
          - staging
```

### 환경 결정 로직

```yaml
env:
  # 브랜치에 따라 환경 결정
  DEPLOY_ENV: ${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}
```

| 브랜치 | 배포 환경 |
|--------|----------|
| `main` | Production |
| 그 외 | Staging |

### 전체 흐름

```mermaid
flowchart TD
    A[main/dev 브랜치 푸시] --> B[환경 설정]
    B --> C[AWS 인증]
    C --> D[ECR 로그인]

    D --> E[Backend 배포]
    D --> F[AI Worker 배포]
    D --> G[Frontend 배포]

    E --> H[Lambda 업데이트]
    F --> I[Lambda 업데이트]
    G --> J[S3 업로드]

    J --> K[CloudFront 캐시 무효화]
    K --> L[✅ 배포 완료]
```

### 각 단계 상세

#### 1. AWS 인증

```yaml
- name: Configure AWS Credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-region: ap-northeast-2
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

**secrets**:
- `AWS_ACCESS_KEY_ID`: AWS IAM 사용자 액세스 키
- `AWS_SECRET_ACCESS_KEY`: AWS IAM 시크릿 키

#### 2. Backend 배포

```yaml
- name: Build & Push Backend
  env:
    ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
    ECR_REPOSITORY: leh-backend
    IMAGE_TAG: ${{ github.sha }}  # 커밋 해시를 태그로
  run: |
    # Docker 이미지 빌드 (x86_64 아키텍처)
    docker buildx build \
      --platform linux/amd64 \
      -f ./backend/Dockerfile.lambda \
      -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG \
      -t $ECR_REGISTRY/$ECR_REPOSITORY:latest \
      --push \
      ./backend

    # Lambda 함수 업데이트
    aws lambda update-function-code \
      --function-name leh-backend \
      --image-uri $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
```

**배포 프로세스**:
1. Docker 이미지 빌드
2. ECR (Amazon Elastic Container Registry)에 푸시
3. Lambda 함수가 새 이미지 사용하도록 업데이트

#### 3. AI Worker 배포

```yaml
- name: Build & Push AI Worker
  env:
    ECR_REPOSITORY: leh-ai-worker
  run: |
    # ARM64 아키텍처로 빌드 (Lambda Graviton2)
    docker buildx build \
      --platform linux/arm64 \      # ← Backend와 다름!
      -f ./ai_worker/Dockerfile.lambda \
      -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG \
      --push \
      ./ai_worker

    aws lambda update-function-code \
      --function-name leh-ai-worker \
      --image-uri $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
```

**왜 ARM64?**:
- AWS Graviton2 프로세서 사용
- 비용 절감 (x86보다 20% 저렴)
- AI Worker는 CPU 작업이 많아서 적합

#### 4. Frontend 배포

```yaml
- name: Build Frontend
  env:
    NEXT_PUBLIC_API_BASE_URL: ${{ secrets.BACKEND_API_URL }}
    NEXT_OUTPUT_EXPORT: 'true'
  run: |
    cd frontend
    npm ci
    npm run build  # Static Export (out/ 폴더 생성)

- name: Deploy Frontend to S3
  run: |
    # 정적 파일 업로드 (긴 캐시)
    aws s3 sync ./out s3://$S3_BUCKET --delete \
      --cache-control "public, max-age=31536000, immutable" \
      --exclude "*.html"

    # HTML 파일 업로드 (짧은 캐시)
    aws s3 sync ./out s3://$S3_BUCKET \
      --cache-control "public, max-age=0, must-revalidate" \
      --include "*.html"

- name: Invalidate CloudFront Cache
  run: |
    aws cloudfront create-invalidation \
      --distribution-id $CF_DIST \
      --paths "/*"
```

**캐시 전략**:
- JS/CSS/이미지: 1년 캐시 (파일명에 해시 포함)
- HTML: 캐시 안 함 (항상 최신 버전)

**CloudFront 무효화**:
- 기존 캐시된 파일 삭제
- 새 배포 즉시 반영

---

## GitHub Secrets 설정

GitHub 저장소 Settings → Secrets에서 설정:

| Secret 이름 | 용도 |
|------------|------|
| `AWS_ACCESS_KEY_ID` | AWS IAM 액세스 키 |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM 시크릿 키 |
| `S3_FRONTEND_BUCKET` | Production S3 버킷 이름 |
| `S3_FRONTEND_BUCKET_STAGING` | Staging S3 버킷 이름 |
| `CLOUDFRONT_DISTRIBUTION_ID` | Production CloudFront ID |
| `CLOUDFRONT_DISTRIBUTION_ID_STAGING` | Staging CloudFront ID |
| `BACKEND_API_URL` | Backend API URL |

---

## 로컬에서 CI 검사하기

### Frontend

```bash
cd frontend
npm run lint      # ESLint 검사
npm test          # Jest 테스트
npm run build     # 빌드 확인
```

### Backend

```bash
cd backend
ruff check .              # Ruff 린팅
pytest                    # 전체 테스트
pytest --cov=app          # 커버리지 포함
```

### AI Worker

```bash
cd ai_worker
ruff check .
pytest --cov=src --cov-fail-under=80
```

---

## 배포 실패 시 대응

### 1. CI 실패

```
❌ Frontend tests failed
```

**해결**:
1. 로컬에서 `npm test` 실행
2. 실패한 테스트 확인
3. 코드 수정 후 다시 푸시

### 2. 빌드 실패

```
❌ Docker build failed
```

**해결**:
1. 로컬에서 Docker 빌드 시도
2. Dockerfile 또는 requirements.txt 확인
3. 의존성 버전 충돌 확인

### 3. Lambda 업데이트 실패

```
❌ Lambda update failed
```

**해결**:
1. AWS 콘솔에서 Lambda 상태 확인
2. IAM 권한 확인
3. ECR 이미지 푸시 성공 여부 확인

---

## 배포 후 확인

### 1. 버전 확인

```bash
# Frontend 버전 (개발자 도구 → Network → HTML 응답 헤더)
x-app-version: abc123...  # 커밋 해시

# Backend 버전
curl https://api.example.com/health
# {"version": "abc123..."}
```

### 2. CloudWatch 로그 확인

```bash
# Backend 로그
aws logs tail /aws/lambda/leh-backend --follow

# AI Worker 로그
aws logs tail /aws/lambda/leh-ai-worker --follow
```

---

## 요약

| 단계 | 트리거 | 내용 |
|------|--------|------|
| **CI** | PR, 푸시 | 린팅 + 테스트 + 빌드 검사 |
| **CD (Staging)** | dev 브랜치 푸시 | Staging 환경에 배포 |
| **CD (Production)** | main 브랜치 푸시 | Production 환경에 배포 |

```
개발 → 푸시 → CI 통과 → PR 병합 → CD 실행 → 배포 완료
```

---

**다음 문서**: [06. 보안 및 인증](06-SECURITY_AUTH.md) - JWT 인증과 역할 기반 권한 시스템을 알아봅니다.
