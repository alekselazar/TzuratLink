import React, { useState, useEffect } from "react";
import { useReaderState } from "./ReaderContext";

const ReaderHighlitedLayer = React.memo(() => {
    const highlightedBoxes = useReaderState((ctx) => ctx.highlightedBoxes);

    const [boxes, setBoxes] = useState(highlightedBoxes);

    useEffect(() => {
        setBoxes(highlightedBoxes);
    }, [highlightedBoxes]);

    return (
        <div className='highlighted-layer'>
            {
                boxes.map((box, i) => (
                    <div
                        key={i}
                        className="highlighted-box"
                        style={{
                            top: box.top,
                            left: box.left,
                            height: box.height,
                            width: box.width,
                        }}
                    />
                ))
            }
        </div>
    );
});

export default ReaderHighlitedLayer;