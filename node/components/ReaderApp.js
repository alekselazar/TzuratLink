import React from 'react';
import PDFReader from './PDFReader';
import '@react-pdf-viewer/core/lib/styles/index.css';

const ReaderApp = ({ component, props }) => {

    const COMPONENTS = {
        'PDFReader': PDFReader
    };

    const ReaderParent = COMPONENTS[component];

    return (
        <ReaderParent {...props} />
    )
};

export default ReaderApp;