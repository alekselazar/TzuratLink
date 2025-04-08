import React, { useState, useMemo } from "react";
import { useReaderState } from "./ReaderContext";

const ReaderBoxesLayer = React.memo(() => {
    const existingBoxes = useReaderState((ctx) => ctx.existingBoxes);
    const setHighlightedBoxes = useReaderState((ctx) => ctx.setHighlightedBoxes);
    const setSefariaRef = useReaderState((ctx) => ctx.setSefariaRef);
    const [onceClicked, setOnceClicked] = useState(false);
    
    const handleHover = (ref) => {
        if (!onceClicked) {
            setHighlightedBoxes(existingBoxes.filter((box, _) => box.sefaria_ref === ref));
        }
    };

    const handleClick = (ref) => {
        setOnceClicked(true);
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
                        onMouseOver={() => handleHover(box.sefaria_ref)}
                        onClick={() => handleClick(box.sefaria_ref)}
                    />
                ))
            }
        </div>
    );
});

export default ReaderBoxesLayer;