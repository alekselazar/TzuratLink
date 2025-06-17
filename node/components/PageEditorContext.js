import React, { useContext, createContext, useRef, useState, useMemo } from 'react';

const PageEditorContext = createContext(null);

export const usePageEditorState = (selector) => {
    const context = useContext(PageEditorContext);
    return selector(context);
};

export const PageStateProvider = ({ pageId, file, lines, boxes, anchors, children }) => {

    const idRef = useRef(pageId);
    const anchorsRef = useRef(anchors)

    const fileBlobUrl = useMemo(() => {
        const bytes = atob(file);

        let len = bytes.length;
        let out = new Uint8Array(len);

        while (len--) {
            out[len] = bytes.charCodeAt(len);
        }

        const blob = new Blob([out], { type: 'image/png' });

        return URL.createObjectURL(blob);
    });

    const [sefariaRef, setSefariaRef] = useState('');
    const [ocrLines, setOcrLines] = useState(lines);
    const [existingBoxes, setExistingBoxes] = useState(boxes);
    const [highlightedBoxes, setHilightedBoxes] = useState([]);
    const [relatedText, setRelatedText] = useState('');
    const [warning, setWarning] = useState('');
    const [sefariaRefChoices, setSefariaRefChoices] = useState([]);

    const contextValue = useMemo(() => (
        {
            sefariaRef,
            ocrLines,
            existingBoxes,
            highlightedBoxes,
            relatedText,
            warning,
            sefariaRefChoices,
            setSefariaRef,
            setOcrLines,
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
        ocrLines,
        existingBoxes,
        highlightedBoxes,
        relatedText,
        warning,
        sefariaRef,
        sefariaRefChoices
    ]);

    return (
        <PageEditorContext.Provider value={contextValue}>
            {children}
        </PageEditorContext.Provider>
    )

};