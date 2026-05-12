import React, { useState, useRef, useEffect } from 'react';

export default function Chat({ uploaded }) {
    const [question, setQuestion] = useState('');
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading]);

    const sendMessage = async () => {
        const q = question.trim();
        if (!q) return;
        setMessages(prev => [...prev, { role: 'user', text: q }]);
        setQuestion('');
        setLoading(true);
        try {
            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: q }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Request failed');
            setMessages(prev => [...prev, { role: 'assistant', text: data.answer }]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', text: 'Error: ' + err.message }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    };

    return (
        <>
            {/* Message area */}
            <div className="flex-1 overflow-y-auto px-5 py-6 space-y-4">
                {messages.length === 0 && !loading && (
                    <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 select-none">
                        <svg className="w-16 h-16 mb-4 text-indigo-500/30" fill="none" stroke="currentColor" strokeWidth="1" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 011.037-.443 48.282 48.282 0 005.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
                        </svg>
                        <p className="text-sm">{uploaded ? 'Documents ready! Ask a question below.' : 'Upload a PDF to get started.'}</p>
                    </div>
                )}

                {messages.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}>
                        <div className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap
              ${msg.role === 'user'
                                ? 'bg-gradient-to-br from-indigo-600 to-violet-600 text-white rounded-br-md'
                                : 'bg-white/[0.06] text-gray-200 border border-white/5 rounded-bl-md'
                            }`}>
                            {msg.text}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start animate-fade-in-up">
                        <div className="bg-white/[0.06] border border-white/5 px-5 py-3 rounded-2xl rounded-bl-md flex items-center gap-2">
                            <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                            <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                            <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            {/* Input bar */}
            <div className="border-t border-white/5 bg-[#0d0d18] px-4 py-3">
                <div className="flex items-center gap-2 max-w-3xl mx-auto">
                    <input
                        type="text"
                        value={question}
                        onChange={e => setQuestion(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask a question about your documents..."
                        className="flex-1 bg-white/[0.05] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500
                       focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition"
                    />
                    <button
                        onClick={sendMessage}
                        disabled={loading || !question.trim()}
                        className={`p-2.5 rounded-xl transition-all duration-200
              ${loading || !question.trim()
                                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                                : 'bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white shadow-lg shadow-indigo-500/25'
                            }`}
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                        </svg>
                    </button>
                </div>
            </div>
        </>
    );
}
