/**
 * Case Detail Frontend Types
 * UI-friendly types with camelCase properties
 */

/**
 * Evidence summary item
 */
export interface EvidenceSummary {
  type: string;
  count: number;
}

/**
 * Recent activity in case timeline
 */
export interface RecentActivity {
  action: string;
  timestamp: string;
  user: string;
}

/**
 * Case member (team member)
 */
export interface CaseMember {
  userId: string;
  userName?: string;
  role: string;
}

/**
 * Case detail for UI consumption (camelCase fields)
 */
export interface CaseDetail {
  id: string;
  title: string;
  clientName?: string;
  description?: string;
  status: string;
  createdAt: string;
  updatedAt: string;
  ownerId: string;
  ownerName?: string;
  ownerEmail?: string;
  evidenceCount: number;
  evidenceSummary: EvidenceSummary[];
  aiSummary?: string;
  aiLabels: string[];
  recentActivities: RecentActivity[];
  members: CaseMember[];
}
