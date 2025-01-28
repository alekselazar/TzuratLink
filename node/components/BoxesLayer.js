import React, { useState, useRef, useEffect } from 'react';
import { usePDFEditorState } from './PDFEditorContext';

const BoxesLayer = React.memo(() => {

    const highlightedBoxes = usePDFEditorState((ctx) => ctx.highlightedBoxes);
    const setHilightedBoxes = usePDFEditorState((ctx) => ctx.setHilightedBoxes);
    const sefariaRef = usePDFEditorState((ctx) => ctx.sefariaRef);
    const setWarning = usePDFEditorState((ctx) => ctx.setWarning);

    const [boxes, setBoxes] = useState(highlightedBoxes);

    useEffect(() => {
        setBoxes(highlightedBoxes);
    }, [highlightedBoxes]);
    
    const [selection, setSelection] = useState(null);
    const [isSelecting, setIsSelecting] = useState(false);

    const boxesLayerRef = useRef(null);
    const startCoords = useRef({ x: 0, y: 0 });
    const currentSelection = useRef(null);

    const handleMouseDown = (event) => {
        if (!boxesLayerRef.current) return;
        if (sefariaRef) {
            setIsSelecting(true);
            const rect = boxesLayerRef.current.getBoundingClientRect();
            const startX = event.clientX - rect.left;
            const startY = event.clientY - rect.top;
            setSelection({ left: startX, top: startY, width: 0, height: 0 });
            startCoords.current = {x: startX, y: startY};

            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);                       
        } else {
            setWarning('You should choose Sefaria ref first');
        }
    };

    const handleMouseMove = (event) => {
        const rect = boxesLayerRef.current.getBoundingClientRect();
        const currentX = event.clientX - rect.left;
        const currentY = event.clientY - rect.top;

        const newLeft = Math.min(startCoords.current.x, currentX);
        const newTop = Math.min(startCoords.current.y, currentY);
        const newWidth = Math.abs(startCoords.current.x - currentX);
        const newHeight = Math.abs(startCoords.current.y - currentY);
        const newSelection = {left: newLeft, top: newTop, width: newWidth, height: newHeight};
        setSelection(newSelection);
        currentSelection.current = newSelection;
    };

    const handleMouseUp = () => {
        if (currentSelection.current && currentSelection.current.width > 0 && currentSelection.current.height > 0) {
            const rect = boxesLayerRef.current.getBoundingClientRect();
            const top = `${(currentSelection.current.top / rect.height) * 100}%`;
            const left = `${(currentSelection.current.left / rect.width) * 100}%`;
            const width = `${(currentSelection.current.width / rect.width) * 100}%`;
            const height = `${(currentSelection.current.height / rect.height) * 100}%`;

            setHilightedBoxes((prev) => [...prev, {top: top, left: left, width: width, height: height}]);
        }
        setIsSelecting(false);
        setSelection(null);
        currentSelection.current = null;

        document.removeEventListener('mousemove', handleMouseMove); 
        document.removeEventListener('mouseup', handleMouseUp);
    };

    const handleContextMenu = (event, index) => {
        event.preventDefault();
        setHilightedBoxes(prev => prev.filter((_, i) => i !== index));
    };

    return (
        <div
            className='boxes-layer'
            onMouseDown={handleMouseDown}
            ref={boxesLayerRef}
        >
            {isSelecting && selection && (
                <div
                    style={{
                        position: 'absolute',
                        top: selection.top,
                        left: selection.left,
                        height: selection.height,
                        width: selection.width,
                        backgroundColor: 'rgba(0, 0, 255, 0.3)',
                        border: '1px solid blue',
                    }}
                />
            )}
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
                        onContextMenu={(e) => handleContextMenu(e, i)}
                    />
                ))
            }
        </div>
    );
});

export default BoxesLayer;