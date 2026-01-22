import React, { useContext, createContext, useState, useRef, useMemo } from "react";

const ReaderContext = createContext(null);

export const useReaderState = (selector) => {
    const context = useContext(ReaderContext);
    return selector(context);
};

export const ReaderStateProvider = ({ pageId, file, boxes, anchors, children }) => {

    const idRef = useRef(pageId);
    const lang = useRef(navigator.language);

    const fileBlobUrl = useMemo(() => {
        if (!file) return null;
        
        const bytes = atob(file);

        let len = bytes.length;
        let out = new Uint8Array(len);

        while (len--) {
            out[len] = bytes.charCodeAt(len);
        }

        const blob = new Blob([out], { type: 'application/pdf' });

        return URL.createObjectURL(blob);
    }, [file]);

    const [sefariaRef, setSefariaRef] = useState('');
    const [highlightedBoxes, setHighlightedBoxes] = useState([]);
    const [hoverBoxes, setHoverBoxes] = useState([]);
    const [existingBoxes, setExistingBoxes] = useState(boxes);
    const [text, setText] = useState('');
    const [related, setRelated] = useState({});
    const [warning, setWarning] = useState('');
    const contextValue = useMemo(() => (
        {
            sefariaRef,
            highlightedBoxes,
            hoverBoxes,
            existingBoxes,
            text,
            related,
            warning,
            setSefariaRef,
            setHighlightedBoxes,
            setHoverBoxes,
            setExistingBoxes,
            setText,
            setRelated,
            setWarning,
            idRef,
            lang,
            fileBlobUrl
        }
    ), [
        sefariaRef,
        highlightedBoxes,
        hoverBoxes,
        existingBoxes,
        text,
        related,
        warning,
        fileBlobUrl
    ]);

    return (
        <ReaderContext.Provider value={contextValue}>
            {children}
        </ReaderContext.Provider>
    )

};