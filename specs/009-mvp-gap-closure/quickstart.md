# Quickstart: MVP 구현 갭 해소

**Feature**: 009-mvp-gap-closure
**Branch**: `009-mvp-gap-closure`
**Date**: 2025-12-09

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for local DynamoDB/Qdrant)
- AWS CLI configured
- PostgreSQL 14+

## Environment Setup

### 1. Clone and switch branch

```bash
git clone https://github.com/KernelAcademy-AICamp/ai-camp-2nd-llm-agent-service-project-2nd.git
cd ai-camp-2nd-llm-agent-service-project-2nd
git checkout 009-mvp-gap-closure
```

### 2. Copy environment file

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Required Environment Variables

```bash
# AWS
AWS_REGION=ap-northeast-2
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/leh_db

# AI Services
OPENAI_API_KEY=sk-your-key
QDRANT_HOST=localhost
QDRANT_PORT=6333

# S3
S3_EVIDENCE_BUCKET=leh-evidence-dev

# DynamoDB
DDB_EVIDENCE_TABLE=leh_evidence_dev
```

## Local Development

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### AI Worker (Local testing)

```bash
cd ai_worker

# Install dependencies
pip install -r requirements.txt

# Run handler locally
python -m handler
```

## Testing

### Backend Tests

```bash
cd backend

# All tests
pytest

# Unit tests only
pytest -m unit

# With coverage
pytest --cov=app --cov-report=html
```

### AI Worker Tests

```bash
cd ai_worker

# All tests
pytest

# Specific parser
pytest tests/src/test_parsers.py -v
```

### Frontend Tests

```bash
cd frontend

# Jest tests
npm test

# Watch mode
npm run test:watch
```

## AWS Setup (Required for full functionality)

### 1. Create S3 Buckets

```bash
aws s3 mb s3://leh-evidence-dev --region ap-northeast-2
aws s3 mb s3://leh-evidence-prod --region ap-northeast-2
```

### 2. Configure Lambda IAM Role

```bash
# Attach S3 policy to Lambda role
aws iam attach-role-policy \
  --role-name leh-ai-worker-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### 3. Configure S3 Event Notification

```bash
aws s3api put-bucket-notification-configuration \
  --bucket leh-evidence-dev \
  --notification-configuration '{
    "LambdaFunctionConfigurations": [{
      "LambdaFunctionArn": "arn:aws:lambda:ap-northeast-2:ACCOUNT:function:leh-ai-worker",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {"Key": {"FilterRules": [{"Name": "prefix", "Value": "cases/"}]}}
    }]
  }'
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/auth/login` | POST | User login |
| `/cases` | GET | List user's cases |
| `/cases/{id}` | GET | Case detail |
| `/cases/{id}/evidence` | GET | Case evidence list |
| `/search?q={query}` | GET | RAG search |
| `/cases/{id}/draft-preview` | POST | Generate draft |
| `/audit-logs` | GET | Audit log list |

## Feature-Specific Commands

### Test AI Worker S3 Integration

```bash
# Upload test file
aws s3 cp test-file.jpg s3://leh-evidence-dev/cases/test-case-id/raw/test-evidence-id_test.jpg

# Check Lambda logs
aws logs tail /aws/lambda/leh-ai-worker --follow
```

### Test RAG Search

```bash
curl -X GET "http://localhost:8000/search?q=폭행&case_id=your-case-id" \
  -H "Authorization: Bearer $TOKEN"
```

### Test Draft Generation

```bash
curl -X POST "http://localhost:8000/cases/your-case-id/draft-preview" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_type": "complaint", "include_citations": true}'
```

## CI/CD

### Run CI locally

```bash
# Backend lint + test
cd backend && ruff check . && pytest

# AI Worker lint + test
cd ai_worker && ruff check . && pytest

# Frontend lint + test
cd frontend && npm run lint && npm test
```

### Deploy to staging

```bash
git push origin 009-mvp-gap-closure
# Create PR to dev
gh pr create --base dev --title "feat(009): MVP Gap Closure"
```

## Troubleshooting

### Backend DB connection error

```bash
# Check PostgreSQL is running
psql -h localhost -U postgres -c "SELECT 1"

# Reset database
cd backend && alembic downgrade base && alembic upgrade head
```

### Qdrant connection error

```bash
# Start local Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Check connection
curl http://localhost:6333/collections
```

### OpenAI API error

```bash
# Verify API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

## US9-11 Feature Verification

### US9: Role Selection at Signup

```bash
# 1. Open signup page
open http://localhost:3000/signup

# 2. Verify role dropdown exists (변호사/의뢰인/탐정)

# 3. Test signup with client role
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "테스트 의뢰인",
    "email": "client@test.com",
    "password": "test1234",
    "role": "client",
    "accept_terms": true,
    "accept_privacy": true
  }'

# Expected: User created with role=client
```

### US10: Client Portal Evidence Upload

```bash
# 1. Login as client
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"client@test.com","password":"test1234"}' | jq -r '.token')

# 2. Upload evidence (should be pending_review)
curl -X POST http://localhost:8000/cases/{case_id}/evidence \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.jpg"

# Expected: review_status = "pending_review"

# 3. Verify access control (should get 403 for other cases)
curl -X GET http://localhost:8000/cases/other-case-id \
  -H "Authorization: Bearer $TOKEN"

# Expected: 403 Forbidden
```

### US11: Detective Portal EXIF + Earnings

```bash
# 1. Login as detective
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"detective@test.com","password":"test1234"}' | jq -r '.token')

# 2. Upload image with EXIF
curl -X POST http://localhost:8000/cases/{case_id}/evidence \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@photo_with_gps.jpg"

# 3. Get EXIF metadata
curl -X GET http://localhost:8000/detective/evidence/{evidence_id}/exif \
  -H "Authorization: Bearer $TOKEN"

# Expected: gps_latitude, gps_longitude, datetime_original

# 4. Check earnings
curl -X GET http://localhost:8000/detective/earnings \
  -H "Authorization: Bearer $TOKEN"

# Expected: total_earned, earnings list
```

## Success Verification

After setup, verify:

1. ✅ Backend starts without errors: `http://localhost:8000/health`
2. ✅ Frontend loads: `http://localhost:3000`
3. ✅ Tests pass: `pytest` and `npm test`
4. ✅ S3 upload triggers Lambda (check CloudWatch logs)
5. ✅ RAG search returns results
6. ✅ Draft generation completes within 30 seconds
7. ✅ Signup page shows role dropdown (US9)
8. ✅ Client portal restricts to assigned cases (US10)
9. ✅ Client evidence shows "검토 대기" status (US10)
10. ✅ Detective EXIF extraction works (US11)
11. ✅ Detective earnings page displays data (US11)
