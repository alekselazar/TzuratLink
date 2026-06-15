import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

function getCsrf() {
    const meta = typeof document !== 'undefined'
        ? document.querySelector('meta[name="csrf-token"]')
        : null;
    return meta ? meta.content : '';
}

async function authFetch(url, options = {}) {
    const res = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrf(),
            ...(options.headers || {}),
        },
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Request failed');
    return data;
}

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/auth/me')
            .then(r => r.ok ? r.json() : null)
            .then(data => { setUser(data); setLoading(false); })
            .catch(() => setLoading(false));
    }, []);

    const signup = async (email, password, name) => {
        const data = await authFetch('/api/auth/signup', {
            method: 'POST',
            body: JSON.stringify({ email, password, name }),
        });
        setUser(data);
        return data;
    };

    const login = async (email, password) => {
        const data = await authFetch('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        setUser(data);
        return data;
    };

    const logout = async () => {
        await authFetch('/api/auth/logout', { method: 'POST' });
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, signup, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
