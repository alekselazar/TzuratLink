import React from 'react';
import { PDFStateProvider } from './PDFEditorContext';
import EditedPDFView from './EditedPDFView';
import PDFRefsView from './PDFRefsView';

const PDFEditor = (props) => {

    return (
        <PDFStateProvider {...props}>
            <div style={{ display: 'flex', width: '100%' }}>
                <div style={{ width: '75%', position: 'relative' }}>
                    <EditedPDFView />
                </div>
                <div style={{ width: '25%', padding: '20px' }}>
                    <PDFRefsView />                    
                </div>
            </div>
        </PDFStateProvider>
    );
};

export default PDFEditor;