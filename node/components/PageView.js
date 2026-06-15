import React, { useState } from 'react';
import { useReaderState } from './ReaderContext';

function buildWordChunks(words, tags, segments) {
    const segMap = new Array(words.length).fill(null);
    for (const seg of segments) {
        for (let i = seg.start; i < seg.end; i++) {
            segMap[i] = seg.sefaria_ref;
        }
    }
    const chunks = [];
    let i = 0;
    while (i < words.length) {
        const ref = segMap[i];
        let j = i + 1;
        while (j < words.length && segMap[j] === ref) j++;
        chunks.push({ sefaria_ref: ref, words: words.slice(i, j), tags: tags.slice(i, j) });
        i = j;
    }
    return chunks;
}

const renderWord = (word, tag, key) => {
    const text = word + ' ';
    return tag ? React.createElement(tag, { key }, text) : <React.Fragment key={key}>{text}</React.Fragment>;
};

const TextSegment = React.memo(({ chunk, isSelected, isHovered, onMouseEnter, onMouseLeave, onClick }) => {
    const cls = ['segment', isSelected && 'segment--selected', isHovered && 'segment--hovered']
        .filter(Boolean).join(' ');
    return (
        <span className={cls} onMouseEnter={onMouseEnter} onMouseLeave={onMouseLeave} onClick={onClick}>
            {chunk.words.map((word, i) => renderWord(word, chunk.tags[i], i))}
        </span>
    );
});

const TextLine = React.memo(({ line, sefariaRef, hoveredRef, setHoveredRef, setSefariaRef }) => {
    const chunks = buildWordChunks(line.words, line.tags, line.segments);
    const cls = line.class_names?.length ? line.class_names.join(' ') : undefined;
    return (
        <span className={cls}>
            {chunks.map((chunk, idx) => {
                if (!chunk.sefaria_ref) {
                    return (
                        <React.Fragment key={idx}>
                            {chunk.words.map((word, i) => renderWord(word, chunk.tags[i], i))}
                        </React.Fragment>
                    );
                }
                return (
                    <TextSegment
                        key={idx}
                        chunk={chunk}
                        isSelected={chunk.sefaria_ref === sefariaRef}
                        isHovered={chunk.sefaria_ref === hoveredRef && chunk.sefaria_ref !== sefariaRef}
                        onMouseEnter={() => setHoveredRef(chunk.sefaria_ref)}
                        onMouseLeave={() => setHoveredRef(null)}
                        onClick={() => setSefariaRef(chunk.sefaria_ref)}
                    />
                );
            })}
        </span>
    );
});

const TextBlock = React.memo(({ block, sefariaRef, hoveredRef, setHoveredRef, setSefariaRef }) => {
    const cls = block.class_names?.length ? block.class_names.join(' ') : undefined;
    return (
        <div className={cls}>
            {(block.lines || []).map((line, idx) => (
                <TextLine
                    key={idx}
                    line={line}
                    sefariaRef={sefariaRef}
                    hoveredRef={hoveredRef}
                    setHoveredRef={setHoveredRef}
                    setSefariaRef={setSefariaRef}
                />
            ))}
        </div>
    );
});

const PageView = () => {
    const blocks = useReaderState((ctx) => ctx.blocks);
    const sefariaRef = useReaderState((ctx) => ctx.sefariaRef);
    const setSefariaRef = useReaderState((ctx) => ctx.setSefariaRef);
    const [hoveredRef, setHoveredRef] = useState(null);

    return (
        <div className="page-content">
            {(blocks || []).map((block, idx) => (
                <TextBlock
                    key={idx}
                    block={block}
                    sefariaRef={sefariaRef}
                    hoveredRef={hoveredRef}
                    setHoveredRef={setHoveredRef}
                    setSefariaRef={setSefariaRef}
                />
            ))}
        </div>
    );
};

export default PageView;
