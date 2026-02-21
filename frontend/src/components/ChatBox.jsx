import React, { useState, useEffect, useRef } from 'react';
import './ChatBox.css';

const API_URL = 'http://localhost:8000';

const ChatBox = ({ currentUser, recipientId }) => {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        console.log('ChatBox initialized with:', { currentUser, recipientId });
        if (!currentUser || !recipientId) {
            console.error('ChatBox missing required props:', { currentUser, recipientId });
        }
    }, [currentUser, recipientId]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const loadMessages = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/messages/list/${recipientId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await response.json();
            if (response.ok) {
                setMessages(data.messages);
            } else {
                console.error('Failed to load messages:', data);
                setError('Failed to load messages');
            }
        } catch (error) {
            console.error('Error loading messages:', error);
            setError('Connection error');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadMessages();
        const interval = setInterval(loadMessages, 5000); // Poll every 5 seconds
        return () => clearInterval(interval);
    }, [recipientId]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!newMessage.trim()) return;

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/messages/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    recipient_id: recipientId,
                    content: newMessage
                })
            });

            if (response.ok) {
                console.log('Message sent successfully');
                setNewMessage('');
                loadMessages();
            } else {
                const errorData = await response.json();
                console.error('Failed to send message:', errorData);
                alert(`Error: ${errorData.detail || 'Failed to send message'}`);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Connection error while sending message');
        }
    };

    const formatTime = (isoString) => {
        return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="chat-box">
            <div className="chat-messages">
                {error ? (
                    <div className="chat-error" style={{ color: '#ef4444', textAlign: 'center', padding: '1rem' }}>
                        {error}
                    </div>
                ) : loading && messages.length === 0 ? (
                    <div className="chat-loading">Loading messages...</div>
                ) : messages.length === 0 ? (
                    <div className="chat-empty">No messages yet. Start the conversation!</div>
                ) : (
                    messages.map((msg) => (
                        <div
                            key={msg.id}
                            className={`message-wrapper ${msg.sender_id === currentUser?.id ? 'sent' : 'received'}`}
                        >
                            <div className="message-content">
                                <p className="message-text">{msg.content}</p>
                                <span className="message-time">{msg.timestamp ? formatTime(msg.timestamp) : '...'}</span>
                            </div>
                        </div>
                    ))
                )}
                <div ref={messagesEndRef} />
            </div>

            <form className="chat-input-area" onSubmit={handleSend}>
                <input
                    type="text"
                    placeholder="Type a message..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                />
                <button type="submit" className="btn-send" disabled={!newMessage.trim()}>
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                </button>
            </form>
        </div>
    );
};

export default ChatBox;
