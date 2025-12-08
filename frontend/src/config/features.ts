/**
 * Feature flags for LEH Lawyer Portal v1
 *
 * Toggle features on/off during development and gradual rollout.
 * Set to `true` when feature is ready for production.
 */

export const FEATURES = {
  // Phase 3: US1 - Party Relationship Graph (P1 MVP)
  // Backend: ✅ Complete (API routes registered)
  PARTY_GRAPH: false,  // Set to true when frontend is ready

  // Phase 4: US4 - Evidence-Party Linking (P1 MVP)
  // Backend: ✅ Complete (API routes registered)
  EVIDENCE_PARTY_LINKS: false,  // Set to true when frontend is ready

  // Phase 5: US5 - Dark Mode Toggle (P2 Amenities)
  DARK_MODE: false,

  // Phase 6: US6 - Global Search / Command Palette (P2 Amenities)
  GLOBAL_SEARCH: false,

  // Phase 7: US7 - Today View Dashboard (P2 Amenities)
  TODAY_VIEW: false,

  // Phase 8: US2 - Asset Sheet / Property Division (P2 Optional)
  ASSET_SHEET: false,

  // Phase 9: US3 - Procedure Stage Tracking (P2 Optional)
  PROCEDURE_STAGES: false,

  // Phase 10: US8 - Summary Card Generation (P3)
  SUMMARY_CARD: false,
} as const;

export type FeatureKey = keyof typeof FEATURES;

/**
 * Check if a feature is enabled
 */
export function isFeatureEnabled(feature: FeatureKey): boolean {
  return FEATURES[feature];
}

/**
 * Feature guard component helper
 * Usage: {isFeatureEnabled('PARTY_GRAPH') && <PartyGraph />}
 */
export function withFeatureFlag<T>(
  feature: FeatureKey,
  enabledValue: T,
  disabledValue: T
): T {
  return isFeatureEnabled(feature) ? enabledValue : disabledValue;
}
