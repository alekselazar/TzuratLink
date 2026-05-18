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
            const matchingBoxes = existingBoxes.filter((box) => box.ref === sefariaRef);
            setHighlightedBoxes(matchingBoxes);
        }
        // Don't clear on sefariaRef change to empty - let hover handle that
    }, [sefariaRef, existingBoxes, setHighlightedBoxes]);

    const handleMouseOver = (ref) => {
        const matchingBoxes = existingBoxes.filter((box) => box.ref === ref);
        if (sefariaRef && sefariaRef === ref) {
            return;
        }
        setHighlightedBoxes(matchingBoxes);
    };

    const handleMouseLeave = (ref) => {
        if (sefariaRef && sefariaRef === ref) {
            setHighlightedBoxes(existingBoxes.filter((box) => box.ref === ref));
        } else {
            setHighlightedBoxes([]);
        }
    };

    const handleClick = (ref) => {
        const matchingBoxes = existingBoxes.filter((box) => box.ref === ref);
        setHighlightedBoxes(matchingBoxes);
        setSefariaRef(ref);
    };

    return (
        <div className="boxes-layer">
            {
                existingBoxes.map((box, i) => (
                    <div
                        key={`${box.ref}-${i}`}
                        className="box"
                        style={{
                            top: box.top,
                            left: box.left,
                            height: box.height,
                            width: box.width
                        }}
                        onMouseOver={() => handleMouseOver(box.ref)}
                        onMouseLeave={() => handleMouseLeave(box.ref)}
                        onClick={() => handleClick(box.ref)}
                    />
                ))
            }
        </div>
    );
});

export default ReaderBoxesLayer;