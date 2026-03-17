import React, { useState, useRef, useEffect } from 'react';
import './DocumentChatbot.css';

const API_URL = 'http://localhost:8000';

export default function DocumentChatbot({ documentId }) {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { role: 'assistant', text: 'Hello! I am your AI Contract Assistant. You can ask me to summarize the document, compare clauses against standard templates, or assess specific risks.' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (isOpen) {
            scrollToBottom();
        }
    }, [messages, isOpen]);

    const handleSend = async () => {
        if (!input.trim() || !documentId) return;

        const userMsg = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
        setLoading(true);

        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_URL}/api/documents/chat/${documentId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userMsg }),
            });
            const data = await res.json();

            if (res.ok) {
                setMessages(prev => [...prev, { role: 'assistant', text: data.response }]);
            } else {
                setMessages(prev => [...prev, { role: 'assistant', text: `Error: ${data.detail || 'Could not reach agent.'}` }]);
            }
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', text: 'Connection error occurred.' }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className={`doc-chatbot-container ${isOpen ? 'open' : 'closed'}`}>
            {!isOpen ? (
                <button className="chatbot-toggle-btn" onClick={() => setIsOpen(true)}>
                    Assistant
                </button>
            ) : (
                <div className="chatbot-window">
                    <div className="chatbot-header">
                        <h3>Contract AI Hub</h3>
                        <button className="close-btn" onClick={() => setIsOpen(false)}>✕</button>
                    </div>

                    <div className="chatbot-messages">
                        {messages.map((msg, idx) => (
                            <div key={idx} className={`chat-bubble ${msg.role}`}>
                                {msg.text}
                            </div>
                        ))}
                        {loading && (
                            <div className="chat-bubble assistant loading">
                                <span className="dot">.</span><span className="dot">.</span><span className="dot">.</span>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <div className="chatbot-input-area">
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask about this contract..."
                            rows={2}
                        />
                        <button onClick={handleSend} disabled={loading || !input.trim()}>
                            ➤
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
