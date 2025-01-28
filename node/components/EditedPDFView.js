import React, { useRef } from 'react';
import { Worker, Viewer, SpecialZoomLevel } from '@react-pdf-viewer/core';
import BoxesLayer from './BoxesLayer';
import EditedLayer from './EditedLayer';
import { usePDFEditorState } from './PDFEditorContext';


const EditedPDFView = React.memo(() => {

    const fileBlobUrl = useRef(usePDFEditorState((ctx) => ctx.fileBlobUrl));
    const renderPage = (props) => (
        <>
            {props.canvasLayer.children}
            <EditedLayer/>
            <BoxesLayer/>
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

export default EditedPDFView;