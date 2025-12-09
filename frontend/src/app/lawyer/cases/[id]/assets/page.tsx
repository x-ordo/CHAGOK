/**
 * Asset Sheet Page
 * US2 - 재산분할표 (Asset Division Sheet)
 *
 * Korean divorce property division calculation page
 * Based on Civil Code Article 839-2
 */

import AssetSheetClient from './AssetSheetClient';

// Required for static export with dynamic routes
export function generateStaticParams() {
  return [{ id: '1' }, { id: '2' }, { id: '3' }];
}

// Allow dynamic routes not listed in generateStaticParams
export const dynamicParams = true;

interface PageProps {
  params: { id: string };
}

export default function AssetSheetPage({ params }: PageProps) {
  return <AssetSheetClient caseId={params.id} />;
}
