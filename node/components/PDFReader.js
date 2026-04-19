import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ReaderStateProvider, useReaderState } from './ReaderContext';
import ReaderPDFView from './ReaderPDFView';
import ReaderRefsPanel from './ReaderRefsPanel';
import PageTitle from './PageTitle';

const PDFLayout = ({ pageRef, hebrewTitle, lang = 'he' }) => {
    
    const sefariaRef = useReaderState((ctx) => ctx.sefariaRef);

    return (
        <>
            <PageTitle pageRef={pageRef} hebrewTitle={hebrewTitle} lang={lang} />
            <div className='pdf-reader' style={{ direction: lang === 'en' ? 'ltr' : 'rtl' }}>
                <div style={{ width: sefariaRef ? '75%' : '100%', position: 'relative' }}>
                    <ReaderPDFView />
                </div>
                <div style={{ width: '25%', padding: '0px 20px', display: sefariaRef ? 'block' : 'none' }}>
                    <ReaderRefsPanel />                    
                </div>
            </div>
        </>
    )
}

const PDFReader = (props) => {
    const params = useParams();
    const [pageData, setPageData] = useState(props);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Handle client-side navigation based on route params
    useEffect(() => {
        if (typeof window === 'undefined') return;
        
        // If we have route params (client-side navigation), fetch data
        if (params.ref && (!props.pageId || props.pathname !== window.location.pathname)) {
            const fetchDataForRoute = async () => {
                try {
                    setLoading(true);
                    // Fetch page data using ref from route
                    const pageResponse = await fetch(`/api/page/${encodeURIComponent(params.ref)}`);
                    if (!pageResponse.ok) {
                        throw new Error('Failed to fetch page data');
                    }
                    const data = await pageResponse.json();
                    setPageData(data);
                    setLoading(false);
                } catch (err) {
                    setError(err.message);
                    setLoading(false);
                }
            };
            fetchDataForRoute();
        } else if (!params.ref && props.initialRef) {
            // Use initial data from server props (SSR/initial load)
            // No need to fetch if we already have data from server
            setPageData(props);
        }
    }, [params.ref, props.initialRef, props.pageId, props.pathname]);

    // Show loading state during CSR fetch (only on client)
    if (typeof window !== 'undefined' && loading) {
        return (
            <div style={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                height: '100vh',
                fontSize: '18px'
            }}>
                Loading page data...
            </div>
        );
    }

    // Show error state if CSR fetch failed (only on client)
    if (typeof window !== 'undefined' && error) {
        return (
            <div style={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                height: '100vh',
                fontSize: '18px',
                color: 'red'
            }}>
                Error: {error}
            </div>
        );
    }

    // Render normally (works for both SSR and CSR). Omit 'ref' and 'hebrew_title' so they're not passed as React reserved props.
    const { ref: serverRef, hebrew_title: serverHebrewTitle, ...providerProps } = pageData;
    
    // Get the actual page ref and hebrew_title
    // Priority: route params > server props > initial props
    const pageRef = params.ref || serverRef || props.initialRef;
    const hebrewTitle = serverHebrewTitle || props.initialHebrewTitle;
    const lang = props.initialLanguage || 'he';
    
    return (
        <ReaderStateProvider 
            {...providerProps}
            initialLanguage={props.initialLanguage}
        >
            <PDFLayout pageRef={pageRef} hebrewTitle={hebrewTitle} lang={lang} />
        </ReaderStateProvider>
    );
};

export default PDFReader;