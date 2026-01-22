import React, { useState, useEffect } from "react";
import { useReaderState } from "./ReaderContext";

const ReaderBoxesLayer = React.memo(() => {
    const existingBoxes = useReaderState((ctx) => ctx.existingBoxes);
    const setHighlightedBoxes = useReaderState((ctx) => ctx.setHighlightedBoxes);
    const sefariaRef = useReaderState((ctx) => ctx.sefariaRef);
    const setSefariaRef = useReaderState((ctx) => ctx.setSefariaRef);
    
    // Sync highlighted boxes when sefariaRef changes (but not on hover)
    useEffect(() => {
        if (sefariaRef) {
            const matchingBoxes = existingBoxes.filter((box) => box.sefaria_ref === sefariaRef);
            setHighlightedBoxes(matchingBoxes);
        }
        // Don't clear on sefariaRef change to empty - let hover handle that
    }, [sefariaRef, existingBoxes, setHighlightedBoxes]);
    
    const handleMouseOver = (ref) => {
        // Highlight all boxes with the same ref
        const matchingBoxes = existingBoxes.filter((box) => box.sefaria_ref === ref);
        // If there's already a selected ref, keep those highlighted, otherwise just show hover
        if (sefariaRef && sefariaRef === ref) {
            // Already selected, keep it highlighted
            return;
        }
        setHighlightedBoxes(matchingBoxes);
    };

    const handleMouseLeave = (ref) => {
        // If this ref is the selected one, keep it highlighted
        if (sefariaRef && sefariaRef === ref) {
            setHighlightedBoxes(existingBoxes.filter((box) => box.sefaria_ref === ref));
        } else {
            // Otherwise, clear the hover highlight
            setHighlightedBoxes([]);
        }
    };

    const handleClick = (ref) => {
        // Highlight all boxes with the same ref and set as selected
        const matchingBoxes = existingBoxes.filter((box) => box.sefaria_ref === ref);
        setHighlightedBoxes(matchingBoxes);
        setSefariaRef(ref);
    };

    return (
        <div className="boxes-layer">
            {
                existingBoxes.map((box, i) => (
                    <div
                        key={`${box.sefaria_ref}-${i}`}
                        className="box"
                        style={{
                            top: box.top,
                            left: box.left,
                            height: box.height,
                            width: box.width
                        }}
                        onMouseOver={() => handleMouseOver(box.sefaria_ref)}
                        onMouseLeave={() => handleMouseLeave(box.sefaria_ref)}
                        onClick={() => handleClick(box.sefaria_ref)}
                    />
                ))
            }
        </div>
    );
});

export default ReaderBoxesLayer;