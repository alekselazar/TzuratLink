import React from 'react';
import { BrowserRouter, Routes, Route, useParams, useLocation } from 'react-router-dom';
import PDFReader from './PDFReader';
import Navigation from './Navigation';

// Component that handles route-based rendering
const RouteHandler = ({ initialComponent, initialProps }) => {
    const location = useLocation();
    const params = useParams();
    
    // If we have initial props from SSR, use them
    // Otherwise, fetch based on current route
    const component = initialComponent || 'PDFReader';
    const rawProps = initialProps || {};
    // Strip 'ref' from props so it's not passed as React's ref (reserved); pass as initialRef for CSR
    const { ref: initialRef, ...props } = rawProps;
    
    // Replace server-rendered navigation with React Router navigation
    React.useEffect(() => {
        const serverNav = document.getElementById('main-nav');
        if (serverNav) {
            serverNav.innerHTML = ''; // Clear server-rendered nav
        }
    }, []);
    
    return (
        <>
            <Navigation />
            <PDFReader {...props} initialRef={initialRef} routeParams={params} pathname={location.pathname} />
        </>
    );
};

const ReaderApp = ({ component, props }) => {
    return (
        <BrowserRouter>
            <Routes>
                {/* Main route - handles /dafyomi/:amud */}
                <Route 
                    path="/dafyomi/:amud?" 
                    element={<RouteHandler initialComponent={component} initialProps={props} />} 
                />
                {/* Root redirects to dafyomi */}
                <Route 
                    path="/" 
                    element={<RouteHandler initialComponent={component} initialProps={props} />} 
                />
                {/* Catch-all for other routes */}
                <Route 
                    path="*" 
                    element={<RouteHandler initialComponent={component} initialProps={props} />} 
                />
            </Routes>
        </BrowserRouter>
    );
};

export default ReaderApp;