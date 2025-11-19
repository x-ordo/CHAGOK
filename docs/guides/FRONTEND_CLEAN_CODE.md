
## Legal Evidence Hub (LEH) — Frontend Clean Code & Pattern Guide

> **대상:** P(Frontend 담당), FE 코드 생성 AI  
> **스택:** React + TypeScript + Tailwind (디자인 토큰 기반)  
> **목적:** 유지보수성 · 확장성 · 품질 · UX 일관성 극대화

---

# 1. 기본 철학 (Core Principles)

## 1.1 Calm Control UX 우선

- 변호사가 **빠르고 안정적으로** 증거·타임라인·초안을 제어할 수 있어야 한다.
- 화려한 UI보다 **예측 가능성, 명확성, 정보 위계(Information Hierarchy)**가 우선.
- 불필요한 시각적 자극을 줄이고 피로도를 최소화한다.

## 1.2 상태 최소화 & 데이터 흐름 단순화

- 서버 상태는 **React Query**를 사용해 캐싱/비동기 관리.
- 로컬 상태는 “화면 내부에서만 필요한 최소 상태”만 유지.
- 전역 상태(Global store)는 가능한 사용하지 않는다.

## 1.3 프레젠테이션과 로직 분리

- UI 컴포넌트 = **presentational**
- 비즈니스 로직 = `hooks/`, `pages/`, API 모듈에서 처리
- 컴포넌트 내부에 API 호출 또는 로직을 섞지 않는다.

## 1.4 API 스펙의 단일 출처

- `docs/API_SPEC.md` + `frontend/src/api` 내 타입 기반 개발
- 타입과 API path는 하드코딩 금지 — 반드시 공용 타입 참조

---

# 2. 폴더 구조 규칙 (Folder Structure)

bash
frontend/src/
  api/          # 백엔드 API 클라이언트 (Axios / Fetch wrapper)
  components/   # 재사용 가능한 UI 컴포넌트
  hooks/        # 재사용 가능한 상태/비즈니스 로직
  pages/        # 페이지 단위 화면
  types/        # 공용 타입 정의 (Case, Evidence, Draft 등)
  styles/       # 글로벌 스타일, Tailwind config, 디자인 토큰
`

---

## 2.1 컴포넌트 분류 규칙

### components/common

- 버튼(Button), 카드(Card), 레이아웃(Layout), 모달(Modal), 로더 등 공용 UI

### components/case

- 사건 리스트, CaseCard, 사건 상세 UI

### components/evidence

- 증거 테이블, 업로드 박스, 미디어 아이콘, 타임라인 아이템 등

### components/draft

- DraftEditor, CitationPanel, DraftToolbar 등

### 규칙

- **컴포넌트는 가능하면 presentational로 유지한다.**
- API 호출 / 비즈니스 로직 / 조건 분기 로직 등은
  → 반드시 `pages/` 또는 `hooks/` 로 이동

---

# 3. 네이밍 & 타입 규칙 (Naming & Types)

## 3.1 TypeScript 인터페이스

타입은 반드시 `types/` 또는 `api/` 내부에서 정의 후 재사용한다.

ts
// types/case.ts
export interface CaseSummary {
  id: string;
  title: string;
  updatedAt: string;
  evidenceCount: number;
  draftStatus: "none" | "partial" | "ready";
}

## 3.2 컴포넌트 파일명 규칙

- 파일명 = 컴포넌트명 (PascalCase)

  - 예: `CaseCard.tsx`, `EvidenceTable.tsx`, `DraftEditor.tsx`

## 3.3 Prop 설계 규칙

- 한 컴포넌트의 props 수는 **5개 이하** 유지
- Boolean props가 늘어나는 순간 컴포넌트 분리 고려
- 옵셔널 props 사용 시 기본값 명확히 설정

---

# 4. UI/UX 디자인 원칙 (FE 전용)

LEH는 “Calm Control” + “법률 도메인 UX”가 핵심이다.

---

## 4.1 정보 위계 (Information Hierarchy)

각 페이지는 다음 구조를 유지해야 한다:

Title
↓
Filters / Actions
↓
Content (Main)
↓
Footer or Supplementary Information

중요도 우선순위:

1. 사건 요약
2. 타임라인
3. 개별 증거 정보
4. 부가 기능

---

## 4.2 피로도 최소화

- 배경: 중명도 그레이/블루톤 (예: `#F7F9FC`, `#EEF2F6`)
- Primary Action은 화면당 1~2개만 강조
- 애니메이션: 부드러운 fade/slide, 과한 모션 금지

---

## 4.3 법률 도메인 특수 UX

- AI 생성 초안에는 **항상 ‘AI 초안’ 라벨 + 책임부인(Disclaimer)** 표시
- 증거 삭제, 사건 종료 등 파괴적 행동에는 **두 단계 확인 모달**
- 긴 텍스트는 **가독성 높게(줄간격·패딩·폰트)** 렌더링

---

# 5. 상태 관리 패턴

## 5.1 서버 상태 – React Query

사건/증거/Draft 등 서버 데이터는 모두 React Query로 관리:

ts
const { data: cases } = useQuery({
  queryKey: ["cases"],
  queryFn: fetchCases,
  staleTime: 60_000, // 1분
});

## 5.2 로컬 상태 – useState / useReducer

로컬 UI 상태만 유지:

- 모달 open 여부
- 선택된 evidence ID
- 현재 활성화된 탭

### 복잡한 UI 상태는 custom hook으로 캡슐화

ts
export function useDraftEditor(caseId: string) {
  const [selectedSection, setSelectedSection] =
    useState<"facts" | "claims">("facts");

  // ...
}

---

# 6. 재사용 가능한 컴포넌트 패턴

## 6.1 예: EvidenceTable

### 책임

- evidence 리스트 정렬 및 표시
- 선택/클릭 이벤트 전달

### Props 및 컴포넌트 예시

ts
interface EvidenceTableProps {
  items: EvidenceSummary[];
  onSelect: (id: string) => void;
}

export const EvidenceTable: React.FC<EvidenceTableProps> = ({ items, onSelect }) => {
  // ...
};

정렬/필터/서버 요청은
**CaseEvidencePage (페이지 컴포넌트)**에서 수행해야 한다.

---

# 7. 보안 / 프라이버시 고려 (Frontend Security)

### 7.1 LocalStorage 사용 제한

- LocalStorage에는 **절대 증거 전문, 초안 전문을 저장하지 않는다.**
- 인증 토큰 외 민감 데이터 저장 금지.

### 7.2 console.log 금지 항목

- 대화 전문, 이름, 개인 정보 등 민감 텍스트 출력 금지
- 디버깅 필요 시 fake/mock 데이터 사용

### 7.3 에러 메시지 규칙

- 백엔드 에러 내용을 그대로 노출하면 안 된다.
- UX 메시지는 **일반적 · 안전한 문구**여야 한다.

---

# 8. 테스트 원칙 (FE Test Strategy)

React Testing Library + Jest 사용.

테스트는 **모양(CSS)**이 아니라 **행동/상태/필수 텍스트**를 검증한다.

### 예시

tsx
it("shows AI disclaimer in draft tab", () => {
  render(<DraftTab />);
  expect(
    screen.getByText(/이 문서는 AI가 생성한 초안이며/i)
  ).toBeInTheDocument();
});

**테스트 가이드라인**

- 중요한 텍스트 존재 여부 확인
- 버튼 클릭 → 모달 표시 등 인터랙션 테스트
- API 요청 mock (MSW 등)으로 플로우 검증

---

# 9. 코드 리뷰 체크리스트 (FE 전용)

- [ ] 컴포넌트/파일 크기가 과도하게 크지 않은가? (SRP 준수)
- [ ] 로직과 뷰가 적절히 분리되었는가?
- [ ] API 타입을 하드코딩하지 않고 `types/api`를 재사용하는가?
- [ ] 주요 UX 규칙(Disclaimer, 삭제 확인 등)을 준수했는가?
- [ ] 민감 데이터가 FE 영역에 남아 있지 않은가?
- [ ] 최소한의 테스트(smoke test)가 추가되었는가?
- [ ] UI/UX 디자인 토큰을 준수했는가?

---

# 결론

이 문서는 LEH Frontend 개발의 **일관성과 유지보수성**을 보장하기 위한 상위 규칙이며,
P(Frontend 담당) 및 FE 관련 AI 생성기는
**여기 정의된 Clean Code & UX 원칙을 절대 기준으로 준수**해야 한다.
