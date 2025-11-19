# Infra and Deployment

`infra/` is the home for deployment automation, Oracle Cloud (OCI) IaC, GitHub Actions workflows, and all operational artifacts.

## Suggested layout

- `ci-cd/` – GitHub Actions or other pipeline definitions that build, test, and release services.
- `terraform/` – Oracle Cloud (OCI) or other cloud module definitions and environment-specific stacks.
- `scripts/` – Helper scripts for deployments, migrations, or diagnostics.
- `docs/` – Architecture diagrams, IAM policy tables, runbooks, or other supporting material.

As the platform grows, add the relevant folder (e.g., `infra/terraform/`), log intended usage here, and keep this README synced with the new pieces.
# Infra

이 디렉터리에는 Terraform, CDK, GitHub Actions 배포 스크립트 등 인프라/배포 관련 리소스를 저장합니다.

## 제안 구조

- `terraform/` – AWS 계정별 IaC 모듈
- `scripts/` – 배포 또는 마이그레이션 자동화 스크립트
- `docs/` – 다이어그램, IAM 정책 표 등 추가 자료

초기에는 비어 있지만, 인프라 작업을 시작하면 관련 파일을 추가하고 README 를 업데이트하세요.
