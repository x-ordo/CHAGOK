/**
 * Case Detail API Types
 * Matches backend /lawyer/cases/{id} response (snake_case)
 */

/**
 * Evidence summary item in case detail
 */
export interface EvidenceSummaryItem {
  type: string;
  count: number;
}

/**
 * Recent activity item in case detail
 */
export interface RecentActivityItem {
  action: string;
  timestamp: string;
  user: string;
}

/**
 * Case member item in case detail
 */
export interface CaseMemberItem {
  userId: string;
  userName?: string;
  role: string;
}

/**
 * API response for case detail (snake_case fields)
 * From GET /lawyer/cases/{case_id}
 */
export interface CaseDetailApiResponse {
  id: string;
  title: string;
  client_name?: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
  owner_id: string;
  owner_name?: string;
  owner_email?: string;
  evidence_count?: number;
  evidence_summary?: EvidenceSummaryItem[];
  ai_summary?: string;
  ai_labels?: string[];
  recent_activities?: RecentActivityItem[];
  members?: CaseMemberItem[];
}
