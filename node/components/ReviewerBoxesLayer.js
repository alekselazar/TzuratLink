import React from "react";
import { useReviewerState } from "./ReviewerContext";

const ReviewerBoxesLayer = React.memo(() => {
    const existingBoxes = useReviewerState((ctx) => ctx.existingBoxes);
    const setHighlightedBoxes = useReviewerState((ctx) => ctx.setHighlightedBoxes);
    const sefariaRef = useReviewerState((ctx) => ctx.sefariaRef);
    const setSefariaRef = useReviewerState((ctx) => ctx.setSefariaRef);
    
    const handleMouseOver = (ref) => {
        setHighlightedBoxes(prev => {
            const newBoxes = existingBoxes.filter((box, _) => box.sefaria_ref === ref);
            return [...prev, ...newBoxes];
        });                
    };

    const handleMouseLeave = (ref) => {
        setHighlightedBoxes(prev => prev.filter((box, _) => box.sefaria_ref !== ref));
        if (sefariaRef && sefariaRef === ref) setHighlightedBoxes(existingBoxes.filter((box, _) => box.sefaria_ref === ref));
    };

    const handleClick = (ref) => {
        setHighlightedBoxes(existingBoxes.filter((box, _) => box.sefaria_ref === ref));
        setSefariaRef(ref);
    };

    return (
        <div className="boxes-layer">
            {
                existingBoxes.map((box, i) => (
                    <div
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

export default ReviewerBoxesLayer;