import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
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
    const params = useParams();
    const navigate = useNavigate();
    const [pageData, setPageData] = useState(props);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Handle client-side navigation based on route params
    useEffect(() => {
        if (typeof window === 'undefined') return;
        
        // If we have route params (client-side navigation), fetch data
        if (params.amud && (!props.pageId || props.pathname !== window.location.pathname)) {
            const fetchDataForRoute = async () => {
                try {
                    setLoading(true);
                    // Get ref based on amud parameter
                    const response = await fetch('https://www.sefaria.org/api/calendars');
                    const json_data = await response.json();
                    let ref = null;
                    for (const item of json_data.calendar_items) {
                        if (item.title.en === 'Daf Yomi') {
                            ref = ':'.join(item.ref.split(' '));
                            break;
                        }
                    }
                    if (ref) {
                        if (params.amud === 'a') {
                            ref += 'a';
                        } else if (params.amud === 'b') {
                            ref += 'b';
                        }
                        // Fetch page data
                        const pageResponse = await fetch(`/api/page/${encodeURIComponent(ref)}`);
                        if (!pageResponse.ok) {
                            throw new Error('Failed to fetch page data');
                        }
                        const data = await pageResponse.json();
                        setPageData(data);
                        setLoading(false);
                    }
                } catch (err) {
                    setError(err.message);
                    setLoading(false);
                }
            };
            fetchDataForRoute();
        } else if (props.csr && props.initialRef) {
            // Original CSR logic (initialRef = Sefaria ref from server, not React ref)
            const fetchData = async () => {
                try {
                    setLoading(true);
                    const response = await fetch(`/api/page/${encodeURIComponent(props.initialRef)}`);
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
    }, [params.amud, props.csr, props.initialRef, props.pageId, props.pathname]);

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

    // Render normally (works for both SSR and CSR). Omit 'ref' so it's never passed as React ref.
    const { ref: _omit, ...providerProps } = pageData;
    return (
        <ReaderStateProvider {...providerProps}>
            <PDFLayout />
        </ReaderStateProvider>
    );
};

export default PDFReader;