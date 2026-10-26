import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useReaderState } from './ReaderContext';
import ReaderHighlightedLayer from './ReaderHighlightedLayer';
import ReaderBoxesLayer from './ReaderBoxesLayer';

const ReaderPDFView = () => {
    const { ref } = useParams();
    const available = useReaderState((ctx) => ctx.available);
    const lang = useReaderState((ctx) => ctx.lang);
    const [loaded, setLoaded] = useState(false);
    const [error, setError] = useState(false);

    if (!ref) return null;

    if (!available) {
        const isRtl = lang.current !== 'en';
        return (
            <div className="reader-page-container">
                <div className="page-scan-pending-banner">
                    {isRtl
                        ? 'הסריקה של דף זה עדיין בהכנה — אפשר כבר לשוחח עם החברותא עליו.'
                        : "We're still preparing the scanned page for this daf — you can chat with the Chavruta about it in the meantime."}
                </div>
            </div>
        );
    }

    const src = `/api/render/${encodeURIComponent(ref)}`;

    return (
        <div className="reader-page-container">
            {!loaded && !error && (
                <div className="page-loading">
                    <div className="page-spinner" />
                </div>
            )}
            {error && (
                <div className="page-loading page-loading--error">
                    Failed to load page image
                </div>
            )}
            <img
                src={src}
                alt="Talmud page"
                className="reader-page-image"
                style={{ display: loaded ? 'block' : 'none' }}
                onLoad={() => setLoaded(true)}
                onError={() => setError(true)}
            />
            {loaded && <ReaderHighlightedLayer />}
            {loaded && <ReaderBoxesLayer />}
        </div>
    );
};

export default ReaderPDFView;
