/**
 * Assets API Client
 * US2 - 재산분할표 (Asset Division Sheet)
 */

import { apiRequest, ApiResponse } from './client';
import type {
  Asset,
  AssetListResponse,
  AssetCreateRequest,
  AssetUpdateRequest,
  DivisionCalculateRequest,
  DivisionSummary,
  AssetSheetSummary,
  AssetCategory,
} from '@/types/asset';

/**
 * Get list of assets for a case
 */
export async function getAssets(
  caseId: string,
  category?: AssetCategory
): Promise<ApiResponse<AssetListResponse>> {
  const params = category ? `?category=${category}` : '';
  return apiRequest<AssetListResponse>(`/cases/${caseId}/assets${params}`, {
    method: 'GET',
  });
}

/**
 * Get a single asset by ID
 */
export async function getAsset(
  caseId: string,
  assetId: string
): Promise<ApiResponse<Asset>> {
  return apiRequest<Asset>(`/cases/${caseId}/assets/${assetId}`, {
    method: 'GET',
  });
}

/**
 * Create a new asset
 */
export async function createAsset(
  caseId: string,
  data: AssetCreateRequest
): Promise<ApiResponse<Asset>> {
  return apiRequest<Asset>(`/cases/${caseId}/assets`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Update an asset
 */
export async function updateAsset(
  caseId: string,
  assetId: string,
  data: AssetUpdateRequest
): Promise<ApiResponse<Asset>> {
  return apiRequest<Asset>(`/cases/${caseId}/assets/${assetId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

/**
 * Delete an asset
 */
export async function deleteAsset(
  caseId: string,
  assetId: string
): Promise<ApiResponse<void>> {
  return apiRequest<void>(`/cases/${caseId}/assets/${assetId}`, {
    method: 'DELETE',
  });
}

/**
 * Calculate property division
 */
export async function calculateDivision(
  caseId: string,
  data: DivisionCalculateRequest = {}
): Promise<ApiResponse<DivisionSummary>> {
  return apiRequest<DivisionSummary>(`/cases/${caseId}/assets/calculate`, {
    method: 'POST',
    body: JSON.stringify({
      plaintiff_ratio: data.plaintiff_ratio ?? 50,
      defendant_ratio: data.defendant_ratio ?? 50,
      include_separate: data.include_separate ?? false,
      notes: data.notes,
    }),
  });
}

/**
 * Get asset sheet summary
 */
export async function getAssetSummary(
  caseId: string
): Promise<ApiResponse<AssetSheetSummary>> {
  return apiRequest<AssetSheetSummary>(`/cases/${caseId}/assets/summary`, {
    method: 'GET',
  });
}

/**
 * Export assets as CSV
 * Returns the URL to download the CSV file
 */
export function getExportUrl(caseId: string): string {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  return `${baseUrl}/cases/${caseId}/assets/export`;
}

/**
 * Download assets as CSV
 */
export async function exportAssets(caseId: string): Promise<void> {
  const url = getExportUrl(caseId);

  // Create a temporary link and trigger download
  const link = document.createElement('a');
  link.href = url;
  link.download = `assets_${caseId}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
