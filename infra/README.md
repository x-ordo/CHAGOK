# Infra and Deployment

`infra/` is the home for deployment automation, Oracle Cloud (OCI) IaC, GitHub Actions workflows, and all operational artifacts.

## Suggested layout

- `ci-cd/` – GitHub Actions or other pipeline definitions that build, test, and release services.
- `terraform/` – Oracle Cloud (OCI) or other cloud module definitions and environment-specific stacks.
- `scripts/` – Helper scripts for deployments, migrations, or diagnostics.
- `docs/` – Architecture diagrams, IAM policy tables, runbooks, or other supporting material.

As the platform grows, add the relevant folder (e.g., `infra/terraform/`), log intended usage here, and keep this README synced with the new pieces.
