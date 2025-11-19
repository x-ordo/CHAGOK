# Core Shared Modules

`core/` hosts the shared libraries, utilities, and configuration that must be consumed across backend, ai_worker, and frontend.

## Purpose

- 공유 라이브러리: 도메인 모델, 타입 정의, 커스텀 예외처럼 여러 서비스에서 재사용하는 코드
- 공통 유틸: 인증, 로깅, 오류 포맷터처럼 모든 레이어가 함께 쓰는 헬퍼
- 공통 설정: env 처리, feature flag, 인터페이스 계약처럼 한 곳에서 관리해야 하는 설정

## Contribution guidelines

1. 정말 여러 서비스에 필요한 로직만 둡니다; 서비스별 책임이 아닌 경우 내부 패키지에 남겨둡니다.
2. 순환 의존을 피하고 계층(contracts → clients → utils) 또는 적절한 모듈로 정리합니다.
3. 새 디렉터리/모듈은 간단한 설명이나 docstring을 달아 두고, 각 소비자에서 어떻게 쓰는지 짧게 기록합니다.
