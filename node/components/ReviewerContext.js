import React, { useContext, createContext, useRef, useState, useMemo } from 'react';


const ReviewerContext = createContext(null);

export const useReviewerState = (selector) => {
    const context = useContext(ReviewerContext);
    return selector(context);
};

export const ReviewStateProvider = ({ pageId, file, boxes, children }) => {

    const idRef = useRef(pageId);

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
            text,
            warning
        ]);

    return (
        <ReviewerContext.Provider value={contextValue}>
            {children}
        </ReviewerContext.Provider>
    )

};