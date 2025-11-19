import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import CaseDetailPage from '@/pages/cases/[id]';

// Case detail page relies on the router query param to know which case is open.
jest.mock('next/router', () => ({
    useRouter: () => ({
        query: { id: 'case-draft-tab' },
    }),
}));

describe('Plan 3.6 - Draft Tab requirements on the case detail page', () => {
    const renderCaseDetail = () => render(<CaseDetailPage />);

    describe('AI disclaimer visibility', () => {
        test('shows the explicit disclaimer that AI generated the draft and lawyers are responsible', () => {
            renderCaseDetail();

            expect(
                screen.getByText(/이 문서는 AI가 생성한 초안이며, 최종 책임은 변호사에게 있습니다\./i),
            ).toBeInTheDocument();
        });
    });

    describe('Zen mode editor shell', () => {
        test('exposes a zen-mode editor surface with no more than one toolbar/panel', () => {
            const { container } = renderCaseDetail();

            const editorSurface = screen.getByTestId('draft-editor-surface');
            expect(editorSurface).toHaveAttribute('data-zen-mode', 'true');

            const toolbarPanels = container.querySelectorAll('[data-testid="draft-toolbar-panel"]');
            expect(toolbarPanels.length).toBeLessThanOrEqual(1);
        });
    });

    describe('Primary generation control', () => {
        test('primary button uses calm-control styling and reveals a loading state after click', () => {
            renderCaseDetail();

            const generateButton = screen.getByRole('button', { name: /초안 (재)?생성/i });
            expect(generateButton).toHaveClass('btn-primary');
            expect(generateButton).not.toBeDisabled();

            fireEvent.click(generateButton);

            expect(generateButton).toBeDisabled();
            expect(screen.getByText(/생성 중/i)).toBeInTheDocument();
        });
    });
});
