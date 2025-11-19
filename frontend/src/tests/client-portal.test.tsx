import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ClientEvidencePortal from '@/pages/portal';

describe('Plan 3.7 - Client Evidence Submission Portal', () => {
    test('renders only the required portal elements: logo, guidance, single upload zone, and feedback area', () => {
        render(<ClientEvidencePortal />);

        expect(screen.getByText(/Legal Evidence Hub/i)).toBeInTheDocument();
        expect(screen.getByText(/안내/)).toBeInTheDocument();

        const uploadZones = screen.getAllByTestId('client-upload-zone');
        expect(uploadZones).toHaveLength(1);

        const feedback = screen.getByTestId('upload-feedback');
        expect(feedback).toBeInTheDocument();
        expect(feedback).toHaveTextContent(/준비/i);
    });

    test('shows success green confirmation after files are uploaded', async () => {
        render(<ClientEvidencePortal />);

        const fileInput = screen.getByLabelText('증거 파일 업로드') as HTMLInputElement;
        const files = [
            new File(['dummy'], 'chat-log.txt', { type: 'text/plain' }),
            new File(['dummy'], 'photo.jpg', { type: 'image/jpeg' }),
        ];

        fireEvent.change(fileInput, { target: { files } });

        await waitFor(() => {
            const successMessage = screen.getByText(/파일 2개가 안전하게 전송되었습니다\./);
            expect(successMessage).toHaveClass('text-success-green');
        });
    });
});
