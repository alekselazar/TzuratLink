import React, { useContext, createContext, useRef, useState, useMemo } from 'react';

const PDFEditorContext = createContext(null);

export const usePDFEditorState = (selector) => {
    const context = useContext(PDFEditorContext);
    return selector(context);
};

export const PDFStateProvider = ({ pageId, file, boxes, anchors, children }) => {

    const idRef = useRef(pageId);
    const anchorsRef = useRef(anchors)

    const fileBlobUrl = useMemo(() => {
        const bytes = atob(file);

        let len = bytes.length;
        let out = new Uint8Array(len);

        while (len--) {
            out[len] = bytes.charCodeAt(len);
        }

        const blob = new Blob([out], { type: 'application/pdf' });

        return URL.createObjectURL(blob);
    });

    const [sefariaRef, setSefariaRef] = useState('');
    const [existingBoxes, setExistingBoxes] = useState(boxes);
    const [highlightedBoxes, setHilightedBoxes] = useState([]);
    const [relatedText, setRelatedText] = useState('');
    const [warning, setWarning] = useState('');
    const [sefariaRefChoices, setSefariaRefChoices] = useState([]);

    const contextValue = useMemo(() => (
        {
            sefariaRef,
            existingBoxes,
            highlightedBoxes,
            relatedText,
            warning,
            sefariaRefChoices,
            setSefariaRef,
            setExistingBoxes,
            setHilightedBoxes,
            setRelatedText,
            setWarning,
            setSefariaRefChoices,
            idRef,
            anchorsRef,
            fileBlobUrl
        }
    ), [
        sefariaRef,
        existingBoxes,
        highlightedBoxes,
        relatedText,
        warning,
        sefariaRef,
        sefariaRefChoices
    ]);

    return (
        <PDFEditorContext.Provider value={contextValue}>
            {children}
        </PDFEditorContext.Provider>
    )

};