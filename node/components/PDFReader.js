import React, { useState, useEffect } from 'react';
import { ReaderStateProvider, useReaderState } from './ReaderContext';
import ReaderPDFView from './ReaderPDFView';
import ReaderRefsPanel from './ReaderRefsPanel';

const PDFLayout = () => {
    
    const sefariaRef = useReaderState((ctx) => ctx.sefariaRef);
    const lang = useReaderState((ctx) => ctx.lang);

    return (
        <div className='pdf-reader' style={{ direction: lang.current.startsWith('en') ? 'ltl' : 'rtl' }}>
            <div style={{ width: sefariaRef ? '75%' : '100%', position: 'relative' }}>
                <ReaderPDFView />
            </div>
            <div style={{ width: '25%', padding: '0px 20px', display: sefariaRef ? 'block' : 'none' }}>
                <ReaderRefsPanel />                    
            </div>
        </div>
    )
}

const PDFReader = (props) => {
    const [pageData, setPageData] = useState(props);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // If CSR is needed, fetch data client-side (only runs on client)
    useEffect(() => {
        if (props.csr && props.ref && typeof window !== 'undefined') {
            const fetchData = async () => {
                try {
                    setLoading(true);
                    const response = await fetch(`/api/page/${encodeURIComponent(props.ref)}`);
                    if (!response.ok) {
                        throw new Error('Failed to fetch page data');
                    }
                    const data = await response.json();
                    setPageData(data);
                    setLoading(false);
                } catch (err) {
                    setError(err.message);
                    setLoading(false);
                }
            };
            fetchData();
        }
    }, [props.csr, props.ref]);

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

    // Render normally (works for both SSR and CSR)
    return (
        <ReaderStateProvider {...pageData}>
            <PDFLayout />
        </ReaderStateProvider>
    );
};

export default PDFReader;