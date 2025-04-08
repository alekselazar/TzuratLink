import React, { useContext, createContext, useState, useMemo } from "react";

const ReaderContext = createContext(null);

export const useReaderState = (selector) => {
    const context = useContext(ReaderContext);
    return selector(context);
};

export const ReaderStateProvider = ({ pageId, file, boxes, children }) => {

    const idRef = useRef(pageId);

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
    const [highlightedBoxes, setHighlightedBoxes] = useState([]);
    const [existingBoxes, setExistingBoxes] = useState(boxes);
    const [text, setText] = useState('');
    const [related, setRelated] = useState({});
    const [warning, setWarning] = useState('');
    const contextValue = useMemo(() => (
        {
            sefariaRef,
            highlightedBoxes,
            existingBoxes,
            text,
            related,
            warning,
            setSefariaRef,
            setHighlightedBoxes,
            setExistingBoxes,
            setText,
            setRelated,
            setWarning,
            idRef,
            fileBlobUrl
        }
    ), [
        sefariaRef,
        highlightedBoxes,
        relatedText,
        warning,
        sefariaRef
    ]);

    return (
        <ReaderContext.Provider value={contextValue}>
            {children}
        </ReaderContext.Provider>
    )

};