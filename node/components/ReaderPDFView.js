import { useState } from 'react';
import { useParams } from 'react-router-dom';
import ReaderHighlitedLayer from './ReaderHighlightedLayer';
import ReaderBoxesLayer from './ReaderBoxesLayer';

const ReaderPDFView = () => {
    const { ref } = useParams();
    const [loaded, setLoaded] = useState(false);
    const [error, setError] = useState(false);

    if (!ref) return null;

    const src = `/api/render/${encodeURIComponent(ref)}`;

    return (
        <div className="reader-page-container">
            {!loaded && !error && (
                <div className="pdf-loading">
                    <div className="pdf-spinner" />
                </div>
            )}
            {error && (
                <div className="pdf-loading" style={{ color: '#c0392b' }}>
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
            {loaded && <ReaderHighlitedLayer />}
            {loaded && <ReaderBoxesLayer />}
        </div>
    );
};

export default ReaderPDFView;
