import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ReaderStateProvider, useReaderState } from './ReaderContext';
import ReaderPDFView from './ReaderPDFView';
import ReaderRefsPanel from './ReaderRefsPanel';

const PDFLayout = ({ lang }) => {
    const sefariaRef = useReaderState((ctx) => ctx.sefariaRef);
    return (
        <div className="pdf-reader" style={{ direction: lang === 'en' ? 'ltr' : 'rtl' }}>
            <div style={{ flex: sefariaRef ? '0 0 75%' : '0 0 100%', position: 'relative', transition: 'flex-basis 0.3s', overflowY: 'auto' }}>
                <ReaderPDFView />
                    <div className="page-copyright">
                        © All rights reserved to Vageshel. Content retrieved from Daf Yomi portal.
                    </div>
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

    if (loading) return <div className="page-loading"><div className="page-spinner" /></div>;
    if (error) return <div className="page-loading page-loading--error">Error: {error}</div>;

    return (
        <ReaderStateProvider {...providerProps} pageRef={params.ref} initialLanguage={initialLanguage}>
            <PDFLayout lang={initialLanguage} />
        </ReaderStateProvider>
    );
};

export default PDFReader;
