import React, { useState } from 'react';
import Upload from './components/Upload.jsx';
import Chat from './components/Chat.jsx';

function App() {
    const [uploaded, setUploaded] = useState(false);

    return (
        <div className="min-h-screen flex flex-col font-sans">
            {/* ── Header ── */}
            <header className="sticky top-0 z-50 backdrop-blur-md bg-[#0d0d18]/80 border-b border-white/5">
                <div className="max-w-6xl mx-auto flex items-center justify-between px-6 py-4">
                    <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-indigo-500/30">
                            D
                        </div>
                        <h1 className="text-xl font-semibold tracking-tight bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
                            DocChat
                        </h1>
                    </div>
                    <span className="text-xs text-gray-500 hidden sm:inline">Private &middot; Local AI &middot; No Cloud</span>
                </div>
            </header>

            {/* ── Main Content ── */}
            <main className="flex-1 flex flex-col lg:flex-row max-w-6xl w-full mx-auto px-4 py-6 gap-6">
                {/* Sidebar – Upload */}
                <aside className="lg:w-80 shrink-0">
                    <Upload onUploadSuccess={() => setUploaded(true)} />
                </aside>

                {/* Chat Area */}
                <section className="flex-1 flex flex-col min-h-[500px] rounded-2xl border border-white/5 bg-[#12121c] overflow-hidden shadow-2xl">
                    <Chat uploaded={uploaded} />
                </section>
            </main>

            {/* ── Footer ── */}
            <footer className="text-center py-4 text-xs text-gray-600">
                &copy; 2026 Local Document Chat &mdash; All processing happens on your machine.
            </footer>
        </div>
    );
}

export default App;
