import { useContext, createContext, useState, useRef, useMemo } from "react";

const ReaderContext = createContext(null);

export const useReaderState = (selector) => {
    const context = useContext(ReaderContext);
    return selector(context);
};

export const ReaderStateProvider = ({ pageRef, pageId, pdfUrl, boxes, anchors, available, initialLanguage, children }) => {
    const idRef = useRef(pageId);

    const lang = useRef(
        initialLanguage
            ? initialLanguage.substring(0, 2).toLowerCase()
            : (typeof window !== 'undefined' ? navigator.language : 'he')
    );

    const [sefariaRef, setSefariaRef] = useState(() => boxes?.[0]?.ref || pageRef || '');
    const [highlightedBoxes, setHighlightedBoxes] = useState([]);
    const [existingBoxes, setExistingBoxes] = useState(boxes);
    const [chatOpen, setChatOpen] = useState(available === false);

    const contextValue = useMemo(() => ({
        pageRef,
        sefariaRef, setSefariaRef,
        highlightedBoxes, setHighlightedBoxes,
        existingBoxes, setExistingBoxes,
        chatOpen, setChatOpen,
        idRef,
        lang,
        pdfUrl,
        available: available !== false,
    }), [pageRef, sefariaRef, highlightedBoxes, existingBoxes, chatOpen, pdfUrl, available]);

    return (
        <ReaderContext.Provider value={contextValue}>
            {children}
        </ReaderContext.Provider>
    );
};
