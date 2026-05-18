import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useParams, useLocation } from 'react-router-dom';
import PDFReader from './PDFReader';
import LibraryHome from './LibraryHome';
import TractateView from './TractateView';

const RouteHandler = ({ initialProps, initialLanguage }) => {
    const location = useLocation();
    const params = useParams();

    React.useEffect(() => {
        const nav = document.getElementById('main-nav');
        if (nav) nav.innerHTML = '';
    }, []);

    const rawProps = initialProps || {};
    const { ref: initialRef, hebrew_title: initialHebrewTitle, ...rest } = rawProps;

    return (
        <>
            <PDFReader
                {...rest}
                initialRef={initialRef}
                initialHebrewTitle={initialHebrewTitle}
                routeParams={params}
                pathname={location.pathname}
                initialLanguage={initialLanguage}
            />
        </>
    );
};

const ReaderApp = ({ props, initialLanguage }) => {
    const lang = (props && props.lang) || initialLanguage || 'he';
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<LibraryHome lang={lang} />} />
                <Route path="/tractate/:name" element={<TractateView />} />
                <Route
                    path="/page/:ref"
                    element={<RouteHandler initialProps={props} initialLanguage={lang} />}
                />
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    );
};

export default ReaderApp;
