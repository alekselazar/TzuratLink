import React, { useState, useEffect } from "react";
import { useReaderState } from "./ReaderContext";

const ReaderRefsPanel = React.memo(() => {

    const sefariaRef = useReaderState((ctx) => ctx.sefariaRef);
    const [text, setText] = useState('');

    useEffect(() => {
        fetch(`https://www.sefaria.org/api/v3/texts/${sefariaRef}?return_format=text_only`).then((res) => {
            if (!res.ok) {
                throw Error('Failed to fetch');
            }
            return res.json();
        }).then((data) => {
            if (data.error) {
                throw Error('Failed to fetch');
            }
            setText(data.versions[0].text);
        }).catch((err) => {
            console.log(err);
        });
    }, [sefariaRef]);

    return (
        <div className="refs-panel">
            {text ? (
                <>
                    <span className="related-text">{text}</span>
                    <a className="sefara-link" href={`https://www.sefaria.org.il/${sefariaRef}?lang=he&with=all&lang2=he`} target="_blank">Read on Sefaria</a>
                </>
            ) : (
                <>
                    <span className="related-text">Click on text</span>
                </>
            )
                
            }
        </div>
    )
});

export default ReaderRefsPanel;