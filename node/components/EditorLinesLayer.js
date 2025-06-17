import React, { useEffect, useState } from 'react';
import { usePageEditorState } from './PageEditorContext';

const EditorLinesLayer = React.memo(() => {

    const mainRef = useRef(null);
    const pageId = usePageEditorState((ctx) => ctx.pageId);
    const setHighlightedBoxes = usePageEditorState((ctx) => ctx.setHighlightedBoxes);
    const setWarning = usePageEditorState((ctx) => ctx.setWarning);
    const [lines, setLines] = useState([]);
    const [splitCoords, setSplitCoords] = useState(null);

    useEffect(() => {

        const fetchLines = async () => {
            try {
                res = await fetch(`/editor/lines/${pageId}`);
                if (!res.ok) throw new Error('Failed to fetch lines');
                data = await res.json();
                if (data.error) throw new Error(data.error);
                setLines(data);
            } catch (err) {
                setWarning(err.message);
                console.error(err);
            }
        }

        fetchLines();

    }, []);

    const handleContextMenu = (event, index) => {
        event.preventDefault();
        const container = mainRef.current;

        const containerRect = container.getBoundingClienRect();
        const divRect = event.currentTarget.getBoundingClienRect();
        const x = event.clientX;
        const y = event.clientY;
        setSplitCoords({
            x: x,
            y: y,
            index: index,
            divTop: divRect.top,
            divBottom: divRect.bottom,
            divLeft: divRect.left,
            divRight: divRect.right,
            containerTop: containerRect.top,
            containerHeight: containerRect.height,
            containerLeft: containerRect.left,
            containerWidth: containerRect.width
        });
    };

    const handleClick = (event, index) => {
        event.preventDefault();
        setHighlightedBoxes(prev => [...prev, lines[index]]);
    };

    const splitHorizontally = (event, index) => {
        event.preventDefault();
        if (!splitCoords) return;

        const splits = [
            {
                top: lines[i].top,
                height: ((splitCoords.y - splitCoords.divTop) / splitCoords.containerHeight) * 100,
                left: lines[i].left,
                width: lines[i].width
            },
            {
                top: ((splitCoords.y - splitCoords.containerTop) / splitCoords.containerHeight) * 100,
                height: ((splitCoords.divBottom - splitCoords.y) / splitCoords.containerHeight) * 100,
                left: lines[i].left,
                width: lines[i].width
            }
        ]

        setLines(prev => {
            const filtered = prev.filter((_, i) => i !== index);
            return [...filtered, ...splits];
        });
        setSplitCoords(null);
    };

    const splitVertically = (event, index) => {
        event.preventDefault();
        if (!splitCoords) return;

        const splits = [
            {
                top: lines[i].top,
                height: lines[i].height,
                left: lines[i].left,
                width: ((splitCoords.x - splitCoords.divLeft) / splitCoords.containerWidth) * 100
            },
            {
                top: lines[i].top,
                height: lines[i].height,
                left: ((splitCoords.x - splitCoords.containerLeft) / splitCoords.containerWidth) * 100,
                width: ((splitCoords.divRight - splitCoords.x) / splitCoords.containerWidth) * 100
            }
        ]

        setLines(prev => {
            const filtered = prev.filter((_, i) => i !== index);
            return [...filtered, ...splits];
        });
        setSplitCoords([]);
    };

    return (
        <div className='lines-layer' ref={mainRef}>
            {
                lines.map((line, i) => (
                    <div
                        className='line'
                        key={i}
                        style={{
                            top: line.top,
                            left: line.left,
                            height: line.height,
                            width: line.width
                        }}
                        onClick={(e) => handleClick(e, i)}
                        onContextMenu={(e) => handleContextMenu(e, i)}
                    />
                ))
            }

            {
                splitCoords && (
                    <div
                        className='context-menu-background'
                        onClick={() => setSplitCoords(null)}
                    >
                        <div
                            className='context-menu'
                            style={{
                                top: splitCoords.y - splitCoords.top,
                                left: splitCoords.x - splitCoords.left,
                            }}
                        >
                            <div onClick={(e) => splitHorizontally(e, splitCoords.index)}>Split horizantally</div>
                            <div onClick={(e) => splitVertically(e, splitCoords.index)}>Split vertically</div>
                        </div>
                    </div>
                )
            }

        </div>
    );
});

export default EditorLinesLayer;