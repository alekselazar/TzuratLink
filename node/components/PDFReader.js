import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ReaderStateProvider, useReaderState } from './ReaderContext';
import ReaderPDFView from './ReaderPDFView';
import ReaderRefsPanel from './ReaderRefsPanel';
import ChatPanel from './ChatPanel';

const PANE_TRANSITION = 'flex-basis 0.3s ease-in-out, opacity 0.3s ease-in-out';

const PDFLayout = ({ lang }) => {
    const sefariaRef = useReaderState((ctx) => ctx.sefariaRef);
    const pageRef = useReaderState((ctx) => ctx.pageRef);
    const chatOpen = useReaderState((ctx) => ctx.chatOpen);
    const setChatOpen = useReaderState((ctx) => ctx.setChatOpen);

    let leftPct = 100;
    let rightPct = 0;
    if (chatOpen) {
        leftPct = 50;
        rightPct = 50;
    } else if (sefariaRef) {
        leftPct = 75;
        rightPct = 25;
    }

    return (
        <div className="pdf-reader" style={{ direction: lang === 'en' ? 'ltr' : 'rtl' }}>
            <div style={{ flex: `0 0 ${leftPct}%`, position: 'relative', transition: PANE_TRANSITION, overflowY: 'auto' }}>
                <ReaderPDFView />
                    <div className="page-copyright">
                        © All rights reserved to Vageshel. Content retrieved from Daf Yomi portal.
                    </div>
            </div>
            <div style={{
                flex: `0 0 ${rightPct}%`,
                opacity: rightPct ? 1 : 0,
                transition: PANE_TRANSITION,
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
            }}>
                {chatOpen ? (
                    <ChatPanel dafRef={decodeURIComponent(pageRef)} lang={lang} onClose={() => setChatOpen(false)} />
                ) : sefariaRef ? (
                    <ReaderRefsPanel />
                ) : null}
            </div>
        </div>
    );
};

const PDFReader = ({ pageId, pdfUrl, boxes, anchors, available, initialRef, initialLanguage }) => {
    const params = useParams();
    const [providerProps, setProviderProps] = useState({
        pageId, pdfUrl, boxes: boxes || [], anchors: anchors || [], available,
    });
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
