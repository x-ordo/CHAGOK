/**
 * Case Detail Mapper
 * Converts API CaseDetail (snake_case) to UI CaseDetail (camelCase)
 *
 * Pattern follows evidenceMapper.ts
 */

import { CaseDetailApiResponse } from '@/lib/api/caseDetail';
import { CaseDetail } from '@/types/caseDetail';

/**
 * Maps API case detail response to frontend CaseDetail type
 * Handles snake_case to camelCase conversion and provides defaults for optional fields
 */
export function mapApiCaseDetailToCaseDetail(api: CaseDetailApiResponse): CaseDetail {
  return {
    id: api.id,
    title: api.title,
    clientName: api.client_name,
    description: api.description,
    status: api.status,
    createdAt: api.created_at,
    updatedAt: api.updated_at,
    ownerId: api.owner_id,
    ownerName: api.owner_name,
    ownerEmail: api.owner_email,
    evidenceCount: api.evidence_count ?? 0,
    evidenceSummary: api.evidence_summary ?? [],
    aiSummary: api.ai_summary,
    aiLabels: api.ai_labels ?? [],
    recentActivities: api.recent_activities ?? [],
    members: api.members ?? [],
  };
}

/**
 * Creates a default/empty CaseDetail for loading states
 */
export function createEmptyCaseDetail(id: string): CaseDetail {
  return {
    id,
    title: '',
    status: 'active',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    ownerId: '',
    evidenceCount: 0,
    evidenceSummary: [],
    aiLabels: [],
    recentActivities: [],
    members: [],
  };
}
