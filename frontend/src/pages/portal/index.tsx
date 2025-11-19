import Head from 'next/head';
import { useCallback, useState } from 'react';
import ClientUploadCard from '@/components/portal/ClientUploadCard';

type UploadStatus = 'idle' | 'success' | 'error';

export default function ClientEvidencePortalPage() {
    const [status, setStatus] = useState<UploadStatus>('idle');
    const [uploadedCount, setUploadedCount] = useState(0);

    const handleFilesSelected = useCallback((files: File[]) => {
        if (files.length === 0) {
            setStatus('error');
            return;
        }

        setUploadedCount(files.length);
        setStatus('success');
    }, []);

    return (
        <div className="min-h-screen bg-gradient-to-b from-calm-grey to-white flex items-center justify-center px-6 py-12">
            <Head>
                <title>의뢰인 증거 제출 | Legal Evidence Hub</title>
            </Head>

            <ClientUploadCard status={status} uploadedCount={uploadedCount} onSelectFiles={handleFilesSelected} />
        </div>
    );
}
