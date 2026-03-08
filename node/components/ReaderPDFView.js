import React from 'react';
import ReaderHighlitedLayer from './ReaderHighlightedLayer';
import ReaderBoxesLayer from './ReaderBoxesLayer';
import { useReaderState } from './ReaderContext';

const ReaderPDFView = React.memo(() => {
    const fileBlobUrl = useReaderState((ctx) => ctx.fileBlobUrl);

    if (!fileBlobUrl) {
        return null;
    }

    return (
        <div className="reader-page-container">
            <img
                src={fileBlobUrl}
                alt="Talmud page"
                className="reader-page-image"
            />
            <ReaderHighlitedLayer />
            <ReaderBoxesLayer />
        </div>
    );
});

export default ReaderPDFView;