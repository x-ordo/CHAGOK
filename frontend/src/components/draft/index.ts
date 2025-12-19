/**
 * Draft components index
 * Exports all draft-related components
 */

export { default as DraftEditor } from './DraftEditor';
export type { DraftEditorProps, DraftEditorRef } from './DraftEditor';

export { default as DraftPreviewPanel } from './DraftPreviewPanel';
export { default as DraftGenerationModal } from './DraftGenerationModal';
export { default as EvidenceTraceabilityPanel } from './EvidenceTraceabilityPanel';
export { LawyerReviewCheckbox } from './LawyerReviewCheckbox';

// Phase B.2: DraftSplitView + Reference Components
export { DraftSplitView, default as DraftSplitViewDefault } from './DraftSplitView';
export type { DraftSplitViewProps, ReferenceTabType } from './DraftSplitView';

export { EvidenceReferenceList } from './EvidenceReferenceList';
export type { EvidenceReferenceListProps } from './EvidenceReferenceList';

export { LSSPKeypointReferenceList } from './LSSPKeypointReferenceList';
export type { LSSPKeypointReferenceListProps } from './LSSPKeypointReferenceList';

export { PrecedentReferenceList } from './PrecedentReferenceList';
export type { PrecedentReferenceListProps } from './PrecedentReferenceList';
