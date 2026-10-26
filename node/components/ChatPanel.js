import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { getCsrf, useAuth } from './AuthContext';

const SESSION_STORAGE_PREFIX = 'chavruta_session:';

const appendToLastMessage = (prev, delta) => {
    const next = [...prev];
    const last = next[next.length - 1];
    next[next.length - 1] = { ...last, content: last.content + delta };
    return next;
};

const finalizeLastMessage = (prev, content, navigateSuggestion) => {
    const next = [...prev];
    next[next.length - 1] = { ...next[next.length - 1], content, navigateSuggestion: navigateSuggestion || null };
    return next;
};

const ChatPanel = ({ dafRef, lang, onClose }) => {
    const isRtl = lang !== 'en';
    const storageKey = SESSION_STORAGE_PREFIX + dafRef;
    const { user, loading: authLoading } = useAuth();
    const navigate = useNavigate();

    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [sending, setSending] = useState(false);
    const sessionIdRef = useRef(null);
    const bottomRef = useRef(null);

    useEffect(() => {
        try {
            sessionIdRef.current = localStorage.getItem(storageKey) || null;
        } catch {
            sessionIdRef.current = null;
        }
    }, [storageKey]);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, sending]);

    const send = async () => {
        const question = input.trim();
        if (!question || sending) return;

        setMessages(prev => [...prev, { role: 'user', content: question }, { role: 'assistant', content: '' }]);
        setInput('');
        setSending(true);

        try {
            const res = await fetch('/api/chavruta/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrf(),
                },
                body: JSON.stringify({
                    daf_ref: dafRef,
                    question,
                    session_id: sessionIdRef.current,
                }),
            });

            if (!res.ok || !res.body) throw new Error('Request failed');

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (!line.trim()) continue;
                    const event = JSON.parse(line);

                    if (event.type === 'session' && event.session_id) {
                        sessionIdRef.current = event.session_id;
                        try { localStorage.setItem(storageKey, event.session_id); } catch {}
                    } else if (event.type === 'token') {
                        setMessages(prev => appendToLastMessage(prev, event.content));
                    } else if (event.type === 'done') {
                        setMessages(prev => finalizeLastMessage(prev, event.answer, event.navigate_suggestion));
                    }
                }
            }
        } catch (err) {
            setMessages(prev => finalizeLastMessage(
                prev,
                isRtl ? 'מצטער, קרתה תקלה. נסה שוב.' : 'Sorry, something went wrong. Please try again.',
                null,
            ));
        } finally {
            setSending(false);
        }
    };

    const onKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            send();
        }
    };

    return (
        <div className="chat-panel" style={{ direction: isRtl ? 'rtl' : 'ltr' }}>
            <div className="chat-panel-header">
                <span className="chat-panel-title">
                    {isRtl ? `חברותא — ${dafRef}` : `Chavruta — ${dafRef}`}
                </span>
                <button className="refs-close-btn" onClick={onClose} title="Close">×</button>
            </div>

            {authLoading ? (
                <div className="chat-messages">
                    <div className="page-spinner" style={{ margin: 'auto' }} />
                </div>
            ) : !user ? (
                <div className="chat-messages">
                    <div className="chat-empty-hint">
                        {isRtl
                            ? 'יש להתחבר כדי לשוחח עם החברותא.'
                            : 'Sign in to chat with the Chavruta.'}
                        <br /><br />
                        <Link className="user-nav__link user-nav__link--signup" to="/login">
                            {isRtl ? 'התחברות' : 'Sign in'}
                        </Link>
                        {'  '}
                        <Link className="user-nav__link" to="/signup">
                            {isRtl ? 'הרשמה' : 'Sign up'}
                        </Link>
                    </div>
                </div>
            ) : (
                <>
                    <div className="chat-messages">
                        {messages.length === 0 && (
                            <div className="chat-empty-hint">
                                {isRtl
                                    ? 'שאל אותי כל דבר על הדף — סיכום, הסבר, תרגום, או השוואת שיטות.'
                                    : 'Ask me anything about this daf — a summary, an explanation, a translation, or a comparison of commentators.'}
                            </div>
                        )}
                        {messages.map((m, i) => (
                            <div key={i} className={`chat-message chat-message--${m.role}`}>
                                {m.role === 'assistant' && !m.content && sending ? (
                                    <div className="page-spinner" />
                                ) : m.role === 'assistant' ? (
                                    <>
                                        <div className="chat-markdown">
                                            <ReactMarkdown>{m.content}</ReactMarkdown>
                                        </div>
                                        {m.navigateSuggestion && (
                                            <button
                                                className="chat-navigate-btn"
                                                onClick={() => navigate(`/page/${encodeURIComponent(m.navigateSuggestion.ref)}`)}
                                            >
                                                {isRtl
                                                    ? `עבור אל ${m.navigateSuggestion.ref} ←`
                                                    : `→ Go to ${m.navigateSuggestion.ref}`}
                                            </button>
                                        )}
                                    </>
                                ) : (
                                    <p>{m.content}</p>
                                )}
                            </div>
                        ))}
                        <div ref={bottomRef} />
                    </div>

                    <div className="chat-input-row">
                        <textarea
                            className="chat-input"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={onKeyDown}
                            placeholder={isRtl ? 'הקלד שאלה...' : 'Type a question...'}
                            rows={2}
                        />
                        <button className="chat-send-btn" onClick={send} disabled={sending || !input.trim()}>
                            {isRtl ? 'שלח' : 'Send'}
                        </button>
                    </div>
                </>
            )}
        </div>
    );
};

export default ChatPanel;
