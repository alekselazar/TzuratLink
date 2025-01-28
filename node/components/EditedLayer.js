import React from 'react';
import { usePDFEditorState } from './PDFEditorContext';

const EditedLayer = React.memo(() => {
    
    const existingBoxes = usePDFEditorState((ctx) => ctx.existingBoxes);

    return (
        <div className='edited-layer'>
            {
                existingBoxes.map((box, i) => (
                    <div
                        key={i}
                        className='edited-box'
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
    )
});

export default EditedLayer;