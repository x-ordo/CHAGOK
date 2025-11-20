export const downloadDraftAsDocx = async (draftText: string, caseId: string): Promise<void> => {
    // TODO: Implement actual API call
    // const response = await fetch(\`/api/cases/\${caseId}/draft/download\`, {
    //     method: 'POST',
    //     body: JSON.stringify({ content: draftText }),
    // });
    // const blob = await response.blob();

    // Mock implementation for now
    console.log(`Downloading draft for case ${caseId}...`);
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Create a dummy blob and trigger download
    const blob = new Blob([draftText], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `draft_${caseId}.docx`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
};
