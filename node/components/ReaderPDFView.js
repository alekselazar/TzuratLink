import React, { useEffect, useRef } from 'react';
import * as pdfjsLib from 'pdfjs-dist';
import ReaderHighlightedLayer from './ReaderHighlightedLayer';
import ReaderBoxesLayer from './ReaderBoxesLayer';
import { useReaderState } from './ReaderContext';

// Use CDN worker matching the installed pdfjs-dist version
pdfjsLib.GlobalWorkerOptions.workerSrc =
    `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

const ReaderPDFView = React.memo(() => {
    const pdfUrl = useReaderState((ctx) => ctx.pdfUrl);
    const canvasRef = useRef(null);

    useEffect(() => {
        if (!pdfUrl || !canvasRef.current) return;

        let cancelled = false;
        const canvas = canvasRef.current;

        pdfjsLib.getDocument(pdfUrl).promise
            .then(pdf => pdf.getPage(1))
            .then(page => {
                if (cancelled) return;
                const viewport = page.getViewport({ scale: 2 });
                canvas.width = viewport.width;
                canvas.height = viewport.height;

                const ctx = canvas.getContext('2d');
                // Suppress all text draw calls so only the image layer is painted
                ctx.fillText = () => {};
                ctx.strokeText = () => {};

                return page.render({ canvasContext: ctx, viewport }).promise;
            })
            .catch(err => console.error('PDF render error:', err));

        return () => { cancelled = true; };
    }, [pdfUrl]);

    if (!pdfUrl) return null;

    return (
        <div className="reader-page-container">
            <canvas ref={canvasRef} className="reader-page-canvas" style={{ width: '100%' }} />
            <ReaderHighlightedLayer />
            <ReaderBoxesLayer />
        </div>
    );
});

export default ReaderPDFView;
