import React, { useRef, useState } from 'react';
import { Viewer, Worker } from '@react-pdf-viewer/core';

const PDFReviewer = ({ pageId, file, boxes }) => {
    
    const [currentRef, setCurrentRef] = useState('');
    const [relatedText, setRelatedText] = useState('');
    const [warning, setWarning] = useState('');

    const base64ToBlob = (data) => {
        const bytes = atob(data);

        let len = bytes.length;
        let out = new Uint8Array(len);

        while (len--) {
            out[len] = bytes.charCodeAt(len);
        }

        return new Blob([out], { type: 'application/pdf' });
    };

    const pdfBlob = useRef(base64ToBlob(file));

    const getCSRFToken = () => {
        const csrfCookie = document.cookie
            .split('; ')
            .find((row) => row.startsWith('csrftoken='));
    
        return csrfCookie ? csrfCookie.split('=')[1] : null;
    };
    

    const handleClick = (newRef) => {
        setCurrentRef(newRef);
        fetch(`https://www.sefaria.org/api/v3/texts/${newRef}`).then((res) => {
            if (!res.ok) throw new Error('Failed to fetch sefaria resource.');
            return res.json();
        }).then((data) => {
            if (data.error) throw new Error(data.error);
            setRelatedText(data.versions[0].text);
        }).catch((err) => {
            console.error(err);
            setCurrentRef('');
            setRelatedText('');
            setWarning(err.message);
        });
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        fetch('/editor/reviewpage/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({
                page_id: pageId
            })
        }).then((res) => {
            return res.json();
        }).then((data) => {
            if (data.error) throw new Error(data.error);
            document.location.href = document.location.href;
        }).catch((err) => {
            console.error(err);
            setWarning(err.message);
        });
    };

    const renderPage = (props) => (
        <>
            {props.canvasLayer.children}
            <div className='boxes-layer'>
                {
                    boxes.map((box, i) => (
                        <div 
                            className='edited-box'
                            style={{
                                position: 'absolute',
                                top: box.top,
                                left: box.left,
                                width: box.width,
                                height: box.height
                            }}
                            onClick={() => handleClick(box.sefaria_ref)}
                        />
                    ))
                }
            </div>
        </>
    );

    return (
        <div style={{ display: 'flex', height: '100vh', width: '100%' }}>
            {/* PDF Viewer on the left half */}
            <div style={{ width: '65%', position: 'relative' }} >
                <Worker workerUrl={`https://unpkg.com/pdfjs-dist@2.16.105/build/pdf.worker.min.js`}>
                    <Viewer
                        fileUrl={URL.createObjectURL(pdfBlob.current)}
                        renderPage={renderPage}
                    />
                </Worker>
            </div>
            <div style={{ width: '35%', padding: '20px' }}>
                <div className='current-ref'>
                    {warning && <p style={{color: 'red'}}>{warning}</p>}
                    {currentRef ? (
                        <>
                            <h3>{currentRef}</h3>
                            <p>{relatedText}</p>
                        </>
                    ) : (
                        <>
                            <p>Please, click on Daf</p>
                        </>
                    )
                    }
                </div>
                <button onClick={handleSubmit}>Review this Page</button>
            </div>
        </div>
    );
};

export default PDFReviewer;