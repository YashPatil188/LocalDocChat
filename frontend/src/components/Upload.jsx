import React, { useState, useRef } from 'react';

export default function Upload({ onUploadSuccess }) {
    const [files, setFiles] = useState([]);
    const [status, setStatus] = useState('');
    const [loading, setLoading] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
    const inputRef = useRef(null);

    const handleFiles = (fileList) => {
        const pdfs = Array.from(fileList).filter(f => f.type === 'application/pdf');
        setFiles(pdfs);
        setStatus(pdfs.length ? `${pdfs.length} PDF(s) selected` : 'Only PDF files are accepted');
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        handleFiles(e.dataTransfer.files);
    };

    const handleUpload = async () => {
        if (files.length === 0) { setStatus('Please select at least one PDF'); return; }
        setLoading(true);
        setStatus('Processing documents...');
        const form = new FormData();
        files.forEach(f => form.append('files', f));
        try {
            const res = await fetch('/upload', { method: 'POST', body: form });
            if (!res.ok) { const d = await res.json(); throw new Error(d.detail || 'Upload failed'); }
            setStatus('Documents processed successfully!');
            setFiles([]);
            if (inputRef.current) inputRef.current.value = '';
            onUploadSuccess && onUploadSuccess();
        } catch (err) {
            setStatus('Error: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="rounded-2xl border border-white/5 bg-[#12121c] p-5 shadow-2xl">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-4">Upload Documents</h2>

            {/* Drop zone */}
            <div
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                onClick={() => inputRef.current?.click()}
                className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition-all duration-200
          ${isDragging
                        ? 'border-indigo-500 bg-indigo-500/10'
                        : 'border-white/10 hover:border-indigo-500/50 hover:bg-white/[0.02]'
                    }`}
            >
                <svg className="mx-auto mb-3 w-10 h-10 text-indigo-400" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
                </svg>
                <p className="text-sm text-gray-400">Drag & drop PDFs here or <span className="text-indigo-400 underline">browse</span></p>
                <input ref={inputRef} type="file" multiple accept=".pdf" onChange={(e) => handleFiles(e.target.files)} className="hidden" />
            </div>

            {/* File list */}
            {files.length > 0 && (
                <ul className="mt-3 space-y-1 text-xs text-gray-400">
                    {files.map((f, i) => (
                        <li key={i} className="truncate">📄 {f.name}</li>
                    ))}
                </ul>
            )}

            {/* Upload button */}
            <button
                onClick={handleUpload}
                disabled={loading || files.length === 0}
                className={`mt-4 w-full py-2.5 rounded-xl text-sm font-medium transition-all duration-200
          ${loading || files.length === 0
                        ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                        : 'bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white shadow-lg shadow-indigo-500/25'
                    }`}
            >
                {loading ? 'Processing...' : 'Upload & Process'}
            </button>

            {/* Status */}
            {status && (
                <p className={`mt-3 text-xs animate-fade-in-up ${status.startsWith('Error') ? 'text-red-400' : 'text-emerald-400'}`}>
                    {status}
                </p>
            )}
        </div>
    );
}
