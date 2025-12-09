/**
 * Asset types for US2 - 재산분할표 (Asset Division Sheet)
 * Korean divorce property division based on Civil Code Article 839-2
 */

// Asset category types
export type AssetCategory =
  | 'real_estate'   // 부동산
  | 'savings'       // 예금/적금
  | 'stocks'        // 주식/증권
  | 'retirement'    // 퇴직금/연금
  | 'vehicle'       // 차량
  | 'insurance'     // 보험
  | 'debt'          // 부채
  | 'other';        // 기타

// Asset ownership types
export type AssetOwnership =
  | 'plaintiff'     // 원고 소유
  | 'defendant'     // 피고 소유
  | 'joint'         // 공동 소유
  | 'third_party';  // 제3자 명의

// Asset nature types (Korean divorce law specific)
export type AssetNature =
  | 'marital'       // 공동재산 (혼인 중 취득)
  | 'separate'      // 특유재산 (혼전, 상속, 증여)
  | 'mixed';        // 혼합재산

// Asset model
export interface Asset {
  id: string;
  case_id: string;
  category: AssetCategory;
  ownership: AssetOwnership;
  nature: AssetNature;
  name: string;
  description?: string;
  acquisition_date?: string;
  acquisition_value?: number;
  current_value: number;
  valuation_date?: string;
  valuation_source?: string;
  division_ratio_plaintiff?: number;
  division_ratio_defendant?: number;
  proposed_allocation?: AssetOwnership;
  evidence_id?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
}

// Asset creation request
export interface AssetCreateRequest {
  category: AssetCategory;
  ownership: AssetOwnership;
  nature?: AssetNature;
  name: string;
  description?: string;
  acquisition_date?: string;
  acquisition_value?: number;
  current_value: number;
  valuation_date?: string;
  valuation_source?: string;
  division_ratio_plaintiff?: number;
  division_ratio_defendant?: number;
  proposed_allocation?: AssetOwnership;
  evidence_id?: string;
  notes?: string;
}

// Asset update request (all fields optional)
export interface AssetUpdateRequest {
  category?: AssetCategory;
  ownership?: AssetOwnership;
  nature?: AssetNature;
  name?: string;
  description?: string;
  acquisition_date?: string;
  acquisition_value?: number;
  current_value?: number;
  valuation_date?: string;
  valuation_source?: string;
  division_ratio_plaintiff?: number;
  division_ratio_defendant?: number;
  proposed_allocation?: AssetOwnership;
  evidence_id?: string;
  notes?: string;
}

// Division calculation request
export interface DivisionCalculateRequest {
  plaintiff_ratio?: number;
  defendant_ratio?: number;
  include_separate?: boolean;
  notes?: string;
}

// Division calculation result
export interface DivisionSummary {
  id: string;
  case_id: string;
  total_marital_assets: number;
  total_separate_plaintiff: number;
  total_separate_defendant: number;
  total_debts: number;
  net_marital_value: number;
  plaintiff_share: number;
  defendant_share: number;
  settlement_amount: number;
  plaintiff_ratio: number;
  defendant_ratio: number;
  plaintiff_holdings: number;
  defendant_holdings: number;
  notes?: string;
  calculated_at: string;
  calculated_by?: string;
}

// Category summary
export interface AssetCategorySummary {
  category: AssetCategory;
  total_value: number;
  count: number;
  plaintiff_value: number;
  defendant_value: number;
  joint_value: number;
}

// Full asset sheet summary
export interface AssetSheetSummary {
  division_summary: DivisionSummary | null;
  category_summaries: AssetCategorySummary[];
  total_assets: number;
}

// Response types
export interface AssetListResponse {
  assets: Asset[];
  total: number;
}

// Helper constants for display
export const ASSET_CATEGORY_LABELS: Record<AssetCategory, string> = {
  real_estate: '부동산',
  savings: '예금/적금',
  stocks: '주식/증권',
  retirement: '퇴직금/연금',
  vehicle: '차량',
  insurance: '보험',
  debt: '부채',
  other: '기타',
};

export const ASSET_OWNERSHIP_LABELS: Record<AssetOwnership, string> = {
  plaintiff: '원고',
  defendant: '피고',
  joint: '공동',
  third_party: '제3자',
};

export const ASSET_NATURE_LABELS: Record<AssetNature, string> = {
  marital: '공동재산',
  separate: '특유재산',
  mixed: '혼합재산',
};

// Helper function to format Korean currency
export function formatKoreanCurrency(amount: number): string {
  if (amount >= 100_000_000) {
    const eok = Math.floor(amount / 100_000_000);
    const man = Math.floor((amount % 100_000_000) / 10_000);
    if (man > 0) {
      return `${eok}억 ${man.toLocaleString()}만원`;
    }
    return `${eok}억원`;
  } else if (amount >= 10_000) {
    const man = Math.floor(amount / 10_000);
    return `${man.toLocaleString()}만원`;
  } else {
    return `${amount.toLocaleString()}원`;
  }
}
