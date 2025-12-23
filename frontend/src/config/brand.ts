/**
 * Brand Configuration
 * Centralized brand naming for the application.
 *
 * Values are loaded from environment variables with fallbacks.
 * Update .env to customize brand naming without code changes.
 */

export const BRAND = {
  /** Primary brand name (e.g., "CHAGOK") */
  name: process.env.NEXT_PUBLIC_BRAND_NAME || 'CHAGOK',

  /** Korean brand name (e.g., "차곡") */
  nameKo: process.env.NEXT_PUBLIC_BRAND_NAME_KO || '차곡',

  /** Full brand name with Korean (e.g., "CHAGOK (차곡)") */
  fullName: process.env.NEXT_PUBLIC_BRAND_FULL_NAME || 'CHAGOK (차곡)',

  /** Brand description */
  description: process.env.NEXT_PUBLIC_BRAND_DESCRIPTION || 'AI 기반 법률 증거 관리 시스템',

  /** Default law firm name for portals */
  defaultFirmName: `${process.env.NEXT_PUBLIC_BRAND_NAME || 'CHAGOK'} 법률사무소`,
} as const;

export type Brand = typeof BRAND;
export default BRAND;
