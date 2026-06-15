import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ReaderStateProvider, useReaderState } from './ReaderContext';
import PageView from './PageView';
import ReaderRefsPanel from './ReaderRefsPanel';

const ReaderLayout = ({ lang }) => {
    const sefariaRef = useReaderState((ctx) => ctx.sefariaRef);
    return (
        <div className="page-reader" style={{ direction: lang === 'en' ? 'ltr' : 'rtl' }}>
            <div className="page-reader__content">
                <PageView />
            </div>
            <div className={`page-reader__panel${sefariaRef ? ' page-reader__panel--visible' : ''}`}>
                <ReaderRefsPanel />
            </div>
        </div>
    );
};

const PageReader = ({ pageId, blocks, initialRef, initialLanguage }) => {
    const params = useParams();
    const [providerProps, setProviderProps] = useState({ pageId, blocks: blocks || [] });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!params.ref) return;
        if (pageId && initialRef === params.ref) return;

        setLoading(true);
        fetch(`/api/page/${encodeURIComponent(params.ref)}`)
            .then(r => { if (!r.ok) throw new Error('Not found'); return r.json(); })
            .then(data => {
                setProviderProps({ pageId: data.pageId, blocks: data.blocks || [] });
                setLoading(false);
            })
            .catch(err => { setError(err.message); setLoading(false); });
    }, [params.ref]);

    if (loading) return <div className="page-loading"><div className="page-spinner" /></div>;
    if (error) return <div className="page-loading page-loading--error">Error: {error}</div>;

    return (
        <ReaderStateProvider {...providerProps} pageRef={params.ref} initialLanguage={initialLanguage}>
            <ReaderLayout lang={initialLanguage} />
            <footer className="page-copyright">
                © All rights reserved to Vageshel. Content retrieved from Daf Yomi portal.
            </footer>
        </ReaderStateProvider>
    );
};

export default PageReader;
