import React from 'react';
import { createPortal } from 'react-dom';
import { BrowserRouter, Routes, Route, Navigate, Link, useParams, useLocation, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import PageReader from './PageReader';
import LoginPage from './LoginPage';
import SignupPage from './SignupPage';
import LibraryHome from './LibraryHome';
import TractateView from './TractateView';

const UserNav = ({ lang }) => {
    const { user, loading, logout } = useAuth();
    const navigate = useNavigate();
    const isHe = lang !== 'en';

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
                <button className="user-nav__btn" onClick={handleLogout}>
                    {isHe ? 'התנתקות' : 'Sign out'}
                </button>
            </div>
        ) : (
            <div className="user-nav">
                <Link className="user-nav__link" to="/login">{isHe ? 'התחברות' : 'Sign in'}</Link>
                <Link className="user-nav__link user-nav__link--signup" to="/signup">
                    {isHe ? 'הרשמה' : 'Sign up'}
                </Link>
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
                <UserNav lang={lang} />
                <Routes>
                    <Route path="/" element={<LibraryHome lang={lang} />} />
                    <Route path="/tractate/:name" element={<TractateView />} />
                    <Route path="/page/:ref" element={<RouteHandler initialProps={props} initialLanguage={lang} />} />
                    <Route path="/login" element={<LoginPage lang={lang} />} />
                    <Route path="/signup" element={<SignupPage lang={lang} />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </AuthProvider>
        </BrowserRouter>
    );
};

export default ReaderApp;
