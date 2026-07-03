import React from 'react';
import { createPortal } from 'react-dom';
import { BrowserRouter, Routes, Route, Navigate, useParams, useLocation, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import PageReader from './PageReader';
import LoginPage from './LoginPage';
import SignupPage from './SignupPage';
import LibraryHome from './LibraryHome';
import TractateView from './TractateView';

const UserNav = () => {
    const { user, loading, logout } = useAuth();
    const navigate = useNavigate();

    const target = typeof document !== 'undefined' ? document.getElementById('main-nav') : null;
    if (!target) return null;

    const handleLogout = async () => {
        await logout();
        navigate('/');
    };

    return createPortal(
        loading ? null : user ? (
            <div className="user-nav">
                <span className="user-nav__name">{user.name || user.email}</span>
                <button className="user-nav__btn" onClick={handleLogout}>Sign out</button>
            </div>
        ) : (
            <div className="user-nav">
                <a className="user-nav__link" href="/login">Sign in</a>
                <a className="user-nav__link user-nav__link--signup" href="/signup">Sign up</a>
            </div>
        ),
        target
    );
};

const RouteHandler = ({ initialProps, initialLanguage }) => {
    const params = useParams();

    const rawProps = initialProps || {};
    const { ref: initialRef, ...rest } = rawProps;

    return (
        <PageReader
            {...rest}
            initialRef={initialRef}
            routeParams={params}
            initialLanguage={initialLanguage}
        />
    );
};

const ReaderApp = ({ props, initialLanguage }) => {
    const lang = (props && props.lang) || initialLanguage || 'he';
    return (
        <BrowserRouter>
            <AuthProvider>
                <UserNav />
                <Routes>
                    <Route path="/" element={<LibraryHome lang={lang} />} />
                    <Route path="/tractate/:name" element={<TractateView />} />
                    <Route path="/page/:ref" element={<RouteHandler initialProps={props} initialLanguage={lang} />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/signup" element={<SignupPage />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </AuthProvider>
        </BrowserRouter>
    );
};

export default ReaderApp;
