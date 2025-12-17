/**
 * Copyright (c) 2024-2025 Legal Evidence Hub. All Rights Reserved.
 * PROPRIETARY AND CONFIDENTIAL - Unauthorized copying prohibited.
 *
 * Code Tracking and Fingerprinting System
 *
 * This module provides mechanisms to:
 * 1. Generate unique build fingerprints
 * 2. Embed watermarks in client-side code
 * 3. Track and verify authorized deployments
 *
 * WARNING: Tampering with this module is a violation of copyright law
 * and will be subject to legal prosecution.
 */

// Build-time constants (replaced during build)
const BUILD_ID = process.env.NEXT_PUBLIC_BUILD_ID || 'dev-local';
const BUILD_TIMESTAMP = process.env.NEXT_PUBLIC_BUILD_TIMESTAMP || new Date().toISOString();
const BUILD_COMMIT = process.env.NEXT_PUBLIC_BUILD_COMMIT || 'unknown';

// Embedded watermark - DO NOT REMOVE OR MODIFY
const WATERMARK = 'LEH-2024-PROPRIETARY-8a7b6c5d4e3f2g1h';
const VERSION = '1.0.0';

/**
 * Generate SHA-256 hash (browser-compatible)
 */
async function sha256(message: string): Promise<string> {
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Get build fingerprint
 */
export async function getBuildFingerprint(): Promise<string> {
  const components = [BUILD_ID, BUILD_TIMESTAMP, BUILD_COMMIT, WATERMARK];
  const combined = components.join('|');
  const hash = await sha256(combined);
  return hash.slice(0, 32);
}

/**
 * Get environment fingerprint (browser characteristics)
 */
export async function getEnvironmentFingerprint(): Promise<string> {
  const envData = {
    userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
    language: typeof navigator !== 'undefined' ? navigator.language : 'unknown',
    platform: typeof navigator !== 'undefined' ? navigator.platform : 'unknown',
    screenResolution: typeof screen !== 'undefined' ? `${screen.width}x${screen.height}` : 'unknown',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  };
  const combined = JSON.stringify(envData);
  const hash = await sha256(combined);
  return hash.slice(0, 32);
}

/**
 * Get license information
 */
export function getLicenseInfo() {
  return {
    product: 'Legal Evidence Hub',
    version: VERSION,
    buildId: BUILD_ID,
    buildTimestamp: BUILD_TIMESTAMP,
    buildCommit: BUILD_COMMIT,
    copyright: 'Copyright (c) 2024-2025 Legal Evidence Hub. All Rights Reserved.',
    licenseType: 'Proprietary',
    trackingEnabled: true,
    watermark: WATERMARK,
  };
}

/**
 * Generate tracking token for API requests
 */
export async function generateTrackingToken(): Promise<{
  token: object;
  signature: string;
}> {
  const buildFp = await getBuildFingerprint();
  const envFp = await getEnvironmentFingerprint();

  const tokenData = {
    build_fp: buildFp,
    env_fp: envFp,
    timestamp: new Date().toISOString(),
    watermark: WATERMARK,
  };

  const tokenJson = JSON.stringify(tokenData, Object.keys(tokenData).sort());
  const signature = await sha256(`tracking:${tokenJson}`);

  return {
    token: tokenData,
    signature: signature.slice(0, 32),
  };
}

/**
 * Add tracking headers to fetch requests
 */
export async function getTrackingHeaders(): Promise<Record<string, string>> {
  const buildFp = await getBuildFingerprint();

  return {
    'X-LEH-Build': buildFp,
    'X-LEH-Client': 'web',
    'X-LEH-Version': VERSION,
  };
}

/**
 * Log copyright notice to console (development only)
 */
export function logCopyrightNotice(): void {
  if (process.env.NODE_ENV === 'development') {
    console.log(
      '%c Legal Evidence Hub %c Proprietary Software ',
      'background: #1a365d; color: #fff; padding: 2px 6px; border-radius: 3px 0 0 3px;',
      'background: #c53030; color: #fff; padding: 2px 6px; border-radius: 0 3px 3px 0;'
    );
    console.log(
      '%cCopyright (c) 2024-2025 Legal Evidence Hub. All Rights Reserved.',
      'color: #718096; font-size: 11px;'
    );
    console.log(
      '%cUnauthorized copying, modification, or distribution is strictly prohibited.',
      'color: #e53e3e; font-size: 11px;'
    );
  }
}

// Embedded code signature - DO NOT REMOVE
const CODE_SIGNATURE = `LEH-SIGNATURE-${WATERMARK}-${VERSION}`;

// Export for verification
export const __signature__ = CODE_SIGNATURE;
