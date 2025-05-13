import React, { useState } from "react";

const TranslationsEditor = ({ sentanceId, sentance }) => {
        
    const [enTranslation, setEnTranslation] = useState('');
    const [heTranslation, setHeTranslation] = useState('');
    const [ruTranslation, setRuTranslation] = useState('');
    const [uaTranslation, setUaTranslation] = useState('');

    const getCSRFToken = () => {
        const csrfCookie = document.cookie
            .split('; ')
            .find((row) => row.startsWith('csrftoken='));
        return csrfCookie ? csrfCookie.split('=')[1] : null;
    };

    const handleSubmit = (event) => {
        event.preventDefault();

        fetch('/editor/translates/', {
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
            document.location.href = document.location.href;
        }).catch((err) => {
            console.error(err);
            return;
        });
    };

    return (
        <>
            <p>{sentance}</p>
            <br/>
            <label>
                English:
            </label>
            <textarea value={enTranslation} onChange={(e) => setEnTranslation(e.target.value)} />
            <br/>
            <label>
                Hebrew:
            </label>
            <textarea value={heTranslation} onChange={(e) => setHeTranslation(e.target.value)} />
            <br/>
            <label>
                Russian:
            </label>
            <textarea value={ruTranslation} onChange={(e) => setRuTranslation(e.target.value)} />
            <br/>
            <label>
                Ukrainian:
            </label>
            <textarea value={uaTranslation} onChange={(e) => setUaTranslation(e.target.value)} />
            <br/>
            <button role="button" onClick={handleSubmit}>Submit</button>
        </>
    );


};

export default TranslationsEditor;