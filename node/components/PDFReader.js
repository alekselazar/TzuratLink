import React from 'react';
import { ReaderStateProvider, useReaderState } from './ReaderContext';
import ReaderPDFView from './ReaderPDFView';
import ReaderRefsPanel from './ReaderRefsPanel';

const PDFLayout = () => {
    
    const sefariaRef = useReaderState((ctx) => ctx.sefariaRef);
    const lang = useReaderState((ctx) => ctx.lang);

    return (
        <div className='pdf-reader' style={{ direction: lang.current.startsWith('en') ? 'ltl' : 'rtl' }}>
            <div style={{ width: sefariaRef ? '75%' : '100%', position: 'relative' }}>
                <ReaderPDFView />
            </div>
            <div style={{ width: '25%', padding: '0px 20px', display: sefariaRef ? 'block' : 'none' }}>
                <ReaderRefsPanel />                    
            </div>
        </div>
    )
}

const PDFReader = (props) => {

    return (
        <ReaderStateProvider {...props}>
            <PDFLayout />
        </ReaderStateProvider>
    );
};

export default PDFReader;