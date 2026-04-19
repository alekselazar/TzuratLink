import React from 'react';
import { BrowserRouter, Routes, Route, useParams, useLocation } from 'react-router-dom';
import PDFReader from './PDFReader';
import Navigation from './Navigation';

// Component that handles route-based rendering
const RouteHandler = ({ initialComponent, initialProps, initialPageRef, initialLanguage }) => {
    const location = useLocation();
    const params = useParams();
    
    // If we have initial props from server, use them
    // Otherwise, fetch based on current route
    const component = initialComponent || 'PDFReader';
    const rawProps = initialProps || {};
    // Strip 'ref' and 'hebrew_title' from props so they're not passed as React reserved props
    const { ref: initialRef, hebrew_title: initialHebrewTitle, ...props } = rawProps;
    
    const currentRef = initialPageRef || params.ref || initialRef;
    const currentHebrewTitle = initialHebrewTitle;
    const lang = initialLanguage || 'he';
    
    // Replace server-rendered navigation with React-rendered navigation
    React.useEffect(() => {
        const serverNav = document.getElementById('main-nav');
        if (serverNav) {
            serverNav.innerHTML = ''; // Clear server-rendered nav
        }
    }, []);
    
    return (
        <>
            <Navigation pageRef={currentRef} lang={lang} />
            <PDFReader 
                {...props} 
                initialRef={initialRef}
                initialHebrewTitle={initialHebrewTitle}
                routeParams={params} 
                pathname={location.pathname}
                initialLanguage={lang}
            />
        </>
    );
};

const ReaderApp = ({ component, props, pageRef, initialLanguage }) => {
    return (
        <BrowserRouter>
            <Routes>
                {/* Page route - handles /page/<ref> */}
                <Route 
                    path="/page/:ref*" 
                    element={<RouteHandler 
                        initialComponent={component} 
                        initialProps={props} 
                        initialPageRef={pageRef}
                        initialLanguage={initialLanguage}
                    />} 
                />
                {/* Root and other routes */}
                <Route 
                    path="*" 
                    element={<RouteHandler 
                        initialComponent={component} 
                        initialProps={props} 
                        initialPageRef={pageRef}
                        initialLanguage={initialLanguage}
                    />} 
                />
            </Routes>
        </BrowserRouter>
    );
};

export default ReaderApp;