import React, { useContext, createContext, useState, useRef, useMemo } from "react";

const ReaderContext = createContext(null);

export const useReaderState = (selector) => {
    const context = useContext(ReaderContext);
    return selector(context);
};

/**
 * Normalize language to 'en' or 'he' (Hebrew for any non-English)
 */
const normalizeLanguage = (langStr) => {
    if (!langStr) return 'he';
    const lang = langStr.toString().toLowerCase().substring(0, 2);
    return lang === 'en' ? 'en' : 'he';
};

export const ReaderStateProvider = ({ pageId, pdfUrl, boxes, anchors, initialLanguage, children }) => {

    const idRef = useRef(pageId);

    // Use initialLanguage from server (Django), otherwise detect from navigator
    const getInitialLanguage = () => {
        if (initialLanguage) {
            return normalizeLanguage(initialLanguage);
        }
        if (typeof window !== 'undefined') {
            return normalizeLanguage(navigator.language);
        }
        return 'he';
    };

    const lang = useRef(getInitialLanguage());

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
            pdfUrl
        }
    ), [
        sefariaRef,
        highlightedBoxes,
        hoverBoxes,
        existingBoxes,
        text,
        related,
        warning,
        pdfUrl
    ]);

    return (
        <ReaderContext.Provider value={contextValue}>
            {children}
        </ReaderContext.Provider>
    )

};