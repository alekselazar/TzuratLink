import React, { useState, useRef, useEffect } from 'react';
import { usePageEditorState } from './PageEditorContext';

const EditorBoxesLayer = React.memo(() => {

    const highlightedBoxes = usePageEditorState((ctx) => ctx.highlightedBoxes);
    const [boxes, setBoxes] = useState(highlightedBoxes);

    useEffect(() => {
        setBoxes(highlightedBoxes);
    }, [highlightedBoxes]);

    return (
        <div
            className='boxes-layer'
        >
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

export default EditorBoxesLayer;