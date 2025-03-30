import React, { useState } from 'react';

const EditorInput = () => {
    const [fileUrl, setFileUrl] = useState('');
    const [anchors, setAnchors] = useState([]);
    const [currentAnchor, setCurrentAnchor] = useState('');
    const [warning, setWarning] = useState('');

    const getCSRFToken = () => {
        const csrfCookie = document.cookie
            .split('; ')
            .find((row) => row.startsWith('csrftoken='));
    
        return csrfCookie ? csrfCookie.split('=')[1] : null;
    };

    const addAnchor = (event) => {
        event.preventDefault();
        setAnchors(prev => [...prev, currentAnchor]);
        setCurrentAnchor('');
    };

    const deleteAnchor = (index) => {
        setAnchors(prev => prev.filter((_, i) => i !== index));
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        fetch('/editor/', {
            method: 'POST',
            headers: {
                "Content-Type": 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({
                'fileUrl': fileUrl,
                'anchors': anchors
            })
        }).then((res) => {
            return res.json();
        }).then((data) => {
            if (data.error) throw new Error(data.error);
            document.location.href = document.location.href;
        }).catch((err) => {
            console.error(err);
            setWarning(err.message);
        });
    };

    return (
        <form>
            {warning && <p style={{color: 'red'}}>{warning}</p>}
            <h3>Please input data for new page</h3>
            <label>File URL:</label>
            <input value={fileUrl} onChange={e => setFileUrl(e.target.value)} />
            <label>Sefaria API Anchors:</label>
            {anchors ? (
                <ul>
                    {
                        anchors.map((anchor, index) => (
                            <li key={index}>
                                <span>{anchor}</span>
                                <button type='button' onClick={() => deleteAnchor(index)}>Delete</button>
                            </li>
                        ))
                    }
                </ul>
            ) : (
                <p>No Anchors Inputed Yet</p>
            )
            }
            <input value={currentAnchor} onChange={e => setCurrentAnchor(e.target.value)} />
            <button type='button' onClick={addAnchor}>Add Anchor</button>
            <br />
            <button onClick={handleSubmit}>Submit</button>
        </form>
    );
};

export default EditorInput;