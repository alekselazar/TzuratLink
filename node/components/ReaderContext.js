import { useContext, createContext, useState, useRef, useMemo } from "react";

const ReaderContext = createContext(null);

export const useReaderState = (selector) => {
    const context = useContext(ReaderContext);
    return selector(context);
};

export const ReaderStateProvider = ({ pageRef, pageId, blocks, initialLanguage, children }) => {
    const idRef = useRef(pageId);

    const lang = useRef(
        initialLanguage
            ? initialLanguage.substring(0, 2).toLowerCase()
            : (typeof window !== 'undefined' ? navigator.language : 'he')
    );

    const [sefariaRef, setSefariaRef] = useState(
        () => blocks?.[0]?.lines?.[0]?.segments?.[0]?.sefaria_ref || ''
    );

    const contextValue = useMemo(() => ({
        pageRef,
        idRef,
        lang,
        blocks,
        sefariaRef,
        setSefariaRef,
    }), [pageRef, blocks, sefariaRef]);

    return (
        <ReaderContext.Provider value={contextValue}>
            {children}
        </ReaderContext.Provider>
    );
};
