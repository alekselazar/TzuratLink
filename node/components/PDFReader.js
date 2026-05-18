import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ReaderStateProvider } from './ReaderContext';
import ReaderPDFView from './ReaderPDFView';
import ReaderRefsPanel from './ReaderRefsPanel';
import { useReaderState } from './ReaderContext';

const PDFLayout = ({ lang }) => {
    const sefariaRef = useReaderState((ctx) => ctx.sefariaRef);
    return (
        <div className="pdf-reader" style={{ direction: lang === 'en' ? 'ltr' : 'rtl' }}>
            <div style={{ flex: sefariaRef ? '0 0 75%' : '0 0 100%', position: 'relative', transition: 'flex-basis 0.3s' }}>
                <ReaderPDFView />
            </div>
            <div style={{ flex: '0 0 25%', display: sefariaRef ? 'flex' : 'none', flexDirection: 'column', overflow: 'hidden' }}>
                <ReaderRefsPanel />
            </div>
        </div>
    );
};

const PDFReader = ({ pageId, pdfUrl, boxes, anchors, initialRef, initialLanguage }) => {
    const params = useParams();
    const [providerProps, setProviderProps] = useState({ pageId, pdfUrl, boxes: boxes || [], anchors: anchors || [] });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!params.ref) return;
        // If server already gave us data for this exact ref, use it
        if (pageId && initialRef === params.ref) return;

        setLoading(true);
        fetch(`/api/page/${encodeURIComponent(params.ref)}`)
            .then(r => { if (!r.ok) throw new Error('Not found'); return r.json(); })
            .then(data => {
                const { ref: _r, ...rest } = data;
                setProviderProps(rest);
                setLoading(false);
            })
            .catch(err => { setError(err.message); setLoading(false); });
    }, [params.ref]);

    if (loading) return (
        <div className="pdf-loading"><div className="pdf-spinner" /></div>
    );
    if (error) return (
        <div className="pdf-loading" style={{ color: '#c0392b' }}>Error: {error}</div>
    );

    return (
        <ReaderStateProvider {...providerProps} pageRef={params.ref} initialLanguage={initialLanguage}>
            <PDFLayout lang={initialLanguage} />
            <footer className="page-copyright">
                © All rights reserved to Vageshel. Content retrieved from Daf Yomi portal.
            </footer>
        </ReaderStateProvider>
    );
};

export default PDFReader;
