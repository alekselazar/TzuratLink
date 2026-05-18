import { useContext, createContext, useState, useRef, useMemo } from "react";

const ReaderContext = createContext(null);

export const useReaderState = (selector) => {
    const context = useContext(ReaderContext);
    return selector(context);
};

export const ReaderStateProvider = ({ pageRef, pageId, pdfUrl, boxes, anchors, initialLanguage, children }) => {
    const idRef = useRef(pageId);

    const lang = useRef(
        initialLanguage
            ? initialLanguage.substring(0, 2).toLowerCase()
            : (typeof window !== 'undefined' ? navigator.language : 'he')
    );

    const [sefariaRef, setSefariaRef] = useState(() => boxes?.[0]?.ref || '');
    const [highlightedBoxes, setHighlightedBoxes] = useState([]);
    const [existingBoxes, setExistingBoxes] = useState(boxes);

    const contextValue = useMemo(() => ({
        pageRef,
        sefariaRef, setSefariaRef,
        highlightedBoxes, setHighlightedBoxes,
        existingBoxes, setExistingBoxes,
        idRef,
        lang,
        pdfUrl,
    }), [pageRef, sefariaRef, highlightedBoxes, existingBoxes, pdfUrl]);

    return (
        <ReaderContext.Provider value={contextValue}>
            {children}
        </ReaderContext.Provider>
    );
};
