import React, { useRef, useState } from "react";

const TranslationsEditor = ({ sentanceId, sentance, en, he, ru, ua }) => {
        
    const [enTranslation, setEnTranslation] = useState(en);
    const [heTranslation, setHeTranslation] = useState(he);
    const [ruTranslation, setRuTranslation] = useState(ru);
    const [uaTranslation, setUaTranslation] = useState(ua);

    const getCSRFToken = () => {
        const csrfCookie = document.cookie
            .split('; ')
            .find((row) => row.startsWith('csrftoken='));
        return csrfCookie ? csrfCookie.split('=')[1] : null;
    };

    const handleSubmit = (event) => {
        event.preventDefault();

        fetch('/translates/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({
                sentance_id: sentanceId,
                en: enTranslation,
                he: heTranslation,
                ru: ruTranslation,
                ua: uaTranslation
            })
        }).then((res) => {
            if (!res.ok) throw new Error('Bad response');
            return res.json();
        }).then((data) => {
            if (data.error) throw new Error(data.error);
            window.location.reload(true);
        }).catch((err) => {
            console.error(err);
            return;
        });
    };

    return (
        <>
            <p>{sentance}</p>
            <label>
                English:
                <textarea value={enTranslation} onChange={(e) => setEnTranslation(e.target.value)} />
            </label>
            <label>
                Hebrew:
                <textarea value={heTranslation} onChange={(e) => setHeTranslation(e.target.value)} />
            </label>
            <label>
                Russian:
                <textarea value={ruTranslation} onChange={(e) => setRuTranslation(e.target.value)} />
            </label>
            <label>
                Ukrainian:
                <textarea value={uaTranslation} onChange={(e) => setUaTranslation(e.target.value)} />
            </label>

            <button role="button" onClick={handleSubmit}>Submit</button>
        </>
    );


};

export default TranslationsEditor;