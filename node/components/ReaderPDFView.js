import React, { useRef } from 'react';
import { Worker, Viewer, SpecialZoomLevel } from '@react-pdf-viewer/core';
import ReaderHighlitedLayer from './ReaderHighlightedLayer';
import ReaderBoxesLayer from './ReaderBoxesLayer';
import { useReaderState } from './ReaderContext';


const ReaderPDFView = React.memo(() => {

    const fileBlobUrl = useRef(useReaderState((ctx) => ctx.fileBlobUrl));
    const renderPage = (props) => (
        <>
            {props.canvasLayer.children}
            <ReaderHighlitedLayer/>
            <ReaderBoxesLayer/>
        </>
    );

    return (
        <Worker workerUrl={`https://unpkg.com/pdfjs-dist@2.16.105/build/pdf.worker.min.js`}>
            <Viewer
                fileUrl={fileBlobUrl.current}
                renderPage={renderPage}
                defaultScale={SpecialZoomLevel.PageWidth}
            />
        </Worker>
    )

});

export default ReaderPDFView;