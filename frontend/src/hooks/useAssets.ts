/**
 * useAssets Hook
 * US2 - 재산분할표 (Asset Division Sheet)
 *
 * Manages asset state and operations for a case
 */

import { useState, useCallback, useEffect } from 'react';
import {
  getAssets,
  getAsset,
  createAsset,
  updateAsset,
  deleteAsset,
  calculateDivision,
  getAssetSummary,
  exportAssets,
} from '@/lib/api/assets';
import type {
  Asset,
  AssetCategory,
  AssetCreateRequest,
  AssetUpdateRequest,
  DivisionCalculateRequest,
  DivisionSummary,
  AssetSheetSummary,
} from '@/types/asset';

interface UseAssetsState {
  assets: Asset[];
  summary: AssetSheetSummary | null;
  selectedAsset: Asset | null;
  loading: boolean;
  calculating: boolean;
  error: string | null;
}

interface UseAssetsReturn extends UseAssetsState {
  // Asset CRUD
  fetchAssets: (category?: AssetCategory) => Promise<void>;
  fetchAsset: (assetId: string) => Promise<Asset | null>;
  addAsset: (data: AssetCreateRequest) => Promise<Asset | null>;
  editAsset: (assetId: string, data: AssetUpdateRequest) => Promise<Asset | null>;
  removeAsset: (assetId: string) => Promise<boolean>;

  // Division calculation
  calculate: (data?: DivisionCalculateRequest) => Promise<DivisionSummary | null>;
  fetchSummary: () => Promise<void>;

  // Export
  downloadCsv: () => Promise<void>;

  // Selection
  selectAsset: (asset: Asset | null) => void;
  clearError: () => void;
}

export function useAssets(caseId: string): UseAssetsReturn {
  const [state, setState] = useState<UseAssetsState>({
    assets: [],
    summary: null,
    selectedAsset: null,
    loading: false,
    calculating: false,
    error: null,
  });

  // Fetch all assets
  const fetchAssets = useCallback(async (category?: AssetCategory) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await getAssets(caseId, category);

      if (response.error) {
        setState(prev => ({ ...prev, loading: false, error: response.error || 'Failed to fetch assets' }));
        return;
      }

      setState(prev => ({
        ...prev,
        assets: response.data?.assets || [],
        loading: false,
      }));
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to fetch assets',
      }));
    }
  }, [caseId]);

  // Fetch single asset
  const fetchAsset = useCallback(async (assetId: string): Promise<Asset | null> => {
    try {
      const response = await getAsset(caseId, assetId);

      if (response.error || !response.data) {
        setState(prev => ({ ...prev, error: response.error || 'Asset not found' }));
        return null;
      }

      return response.data;
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : 'Failed to fetch asset',
      }));
      return null;
    }
  }, [caseId]);

  // Create asset
  const addAsset = useCallback(async (data: AssetCreateRequest): Promise<Asset | null> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await createAsset(caseId, data);

      if (response.error || !response.data) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: response.error || 'Failed to create asset',
        }));
        return null;
      }

      // Add to local state
      setState(prev => ({
        ...prev,
        assets: [...prev.assets, response.data!],
        loading: false,
      }));

      return response.data;
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to create asset',
      }));
      return null;
    }
  }, [caseId]);

  // Update asset
  const editAsset = useCallback(async (
    assetId: string,
    data: AssetUpdateRequest
  ): Promise<Asset | null> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await updateAsset(caseId, assetId, data);

      if (response.error || !response.data) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: response.error || 'Failed to update asset',
        }));
        return null;
      }

      // Update in local state
      setState(prev => ({
        ...prev,
        assets: prev.assets.map(a => a.id === assetId ? response.data! : a),
        selectedAsset: prev.selectedAsset?.id === assetId ? response.data! : prev.selectedAsset,
        loading: false,
      }));

      return response.data;
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to update asset',
      }));
      return null;
    }
  }, [caseId]);

  // Delete asset
  const removeAsset = useCallback(async (assetId: string): Promise<boolean> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await deleteAsset(caseId, assetId);

      if (response.error) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: response.error || 'Failed to delete asset',
        }));
        return false;
      }

      // Remove from local state
      setState(prev => ({
        ...prev,
        assets: prev.assets.filter(a => a.id !== assetId),
        selectedAsset: prev.selectedAsset?.id === assetId ? null : prev.selectedAsset,
        loading: false,
      }));

      return true;
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to delete asset',
      }));
      return false;
    }
  }, [caseId]);

  // Calculate division
  const calculate = useCallback(async (
    data?: DivisionCalculateRequest
  ): Promise<DivisionSummary | null> => {
    setState(prev => ({ ...prev, calculating: true, error: null }));

    try {
      const response = await calculateDivision(caseId, data);

      if (response.error || !response.data) {
        setState(prev => ({
          ...prev,
          calculating: false,
          error: response.error || 'Failed to calculate division',
        }));
        return null;
      }

      // Update summary in state
      setState(prev => ({
        ...prev,
        summary: prev.summary ? {
          ...prev.summary,
          division_summary: response.data!,
        } : {
          division_summary: response.data!,
          category_summaries: [],
          total_assets: prev.assets.length,
        },
        calculating: false,
      }));

      return response.data;
    } catch (err) {
      setState(prev => ({
        ...prev,
        calculating: false,
        error: err instanceof Error ? err.message : 'Failed to calculate division',
      }));
      return null;
    }
  }, [caseId]);

  // Fetch summary
  const fetchSummary = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await getAssetSummary(caseId);

      if (response.error) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: response.error || 'Failed to fetch summary',
        }));
        return;
      }

      setState(prev => ({
        ...prev,
        summary: response.data || null,
        loading: false,
      }));
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to fetch summary',
      }));
    }
  }, [caseId]);

  // Export CSV
  const downloadCsv = useCallback(async () => {
    try {
      await exportAssets(caseId);
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : 'Failed to export assets',
      }));
    }
  }, [caseId]);

  // Select asset
  const selectAsset = useCallback((asset: Asset | null) => {
    setState(prev => ({ ...prev, selectedAsset: asset }));
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // Initial fetch
  useEffect(() => {
    if (caseId) {
      fetchAssets();
      fetchSummary();
    }
  }, [caseId, fetchAssets, fetchSummary]);

  return {
    ...state,
    fetchAssets,
    fetchAsset,
    addAsset,
    editAsset,
    removeAsset,
    calculate,
    fetchSummary,
    downloadCsv,
    selectAsset,
    clearError,
  };
}
