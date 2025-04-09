import React from 'react';
import { ReaderStateProvider } from './ReaderContext';
import ReaderPDFView from './ReaderPDFView';
import ReaderRefsPanel from './ReaderRefsPanel';

const PDFReader = (props) => {

    return (
        <ReaderStateProvider {...props}>
            <div style={{ display: 'flex', width: '100%' }}>
                <div style={{ width: '75%', position: 'relative' }}>
                    <ReaderPDFView />
                </div>
                <div style={{ width: '25%', padding: '20px' }}>
                    <ReaderRefsPanel />                    
                </div>
            </div>
        </ReaderStateProvider>
    );
};

export default PDFReader;