import React, { useEffect, useState } from 'react';
import { usePageEditorState } from './PageEditorContext';

const EditorRefsView = React.memo(() => {

    const {
        sefariaRef,
        highlightedBoxes,
        relatedText,
        sefariaRefChoices,
        warning,
        setSefariaRef,
        setExistingBoxes,
        setHilightedBoxes,
        setRelatedText,
        setWarning,
        setSefariaRefChoices,
        anchorsRef,
        idRef
    } = usePageEditorState((ctx) => ctx);

    const [toTranslate, setToTranslate] = useState(false);

    useEffect(() => {
        const fetchRefsAndLinks = async () => {
            const CATEGORIES = ['Commentary', 'Halakhah', 'Tanakh', 'Talmud', 'Mishnah'];

            try {
                const refs = await Promise.all(
                    anchorsRef.current.map(async (anchor) => {
                        const response = await fetch(`https://www.sefaria.org/api/v3/texts/${anchor}`);
                        if (!response.ok) throw new Error('Failed to fetch Sefaria resources');
                        const data = await response.json();
                        if (data.error) throw new Error(data.error);

                        let refs = [];
                        if (anchor.startsWith('Jerusalem') || anchor.startsWith('Mishnah')) {
                            if (!data.isSpanning) data.spanningRefs = [anchor];
                            for (let i = 0; i < data.spanningRefs.length; i++) {
                                let sliced = data.spanningRefs[i].split(':');
                                let name = sliced.slice(0, sliced.length - 1);
                                let start = parseInt(sliced[sliced.length - 1].split('-')[0]);
                                for (let j = 0; j < data.versions[0].text[i].length; j++) {
                                    refs.push([...name, start + j].join(':'));
                                }
                            }
                        } else if (anchor.startsWith('Tur')) {
                            refs.push(anchor);
                        } else {
                            for (let i = 0; i < data.versions[0].text.length; i++) {
                                refs.push([anchor, i + 1].join(':'));
                            }
                        }
                        return refs;
                    })
                );

                const flattenedRefs = refs.flat();

                const links = await Promise.all(
                    flattenedRefs.map(async (ref) => {
                        const response = await fetch(`https://www.sefaria.org/api/related/${ref}`);
                        if (!response.ok) throw new Error('Failed to fetch related links');
                        const data = await response.json();
                        if (data.error) throw new Error(data.error);
                        return data.links
                            .filter((link) => CATEGORIES.includes(link.category))
                            .map((link) => link.ref);
                    })
                );

                const flattenedLinks = links.flat();

                setSefariaRefChoices([...flattenedRefs, ...flattenedLinks]);
            } catch (error) {
                setWarning(error.message);
                console.error(error);
            }
        };

        fetchRefsAndLinks();
    }, [anchorsRef]);

    const getCSRFToken = () => {
        const csrfCookie = document.cookie
            .split('; ')
            .find((row) => row.startsWith('csrftoken='));
        return csrfCookie ? csrfCookie.split('=')[1] : null;
    };

    const handleSelectRef = (event, index) => {
        event.preventDefault();
        setSefariaRef(sefariaRefChoices[index]);
        fetch(`https://www.sefaria.org/api/v3/texts/${sefariaRefChoices[index]}?return_format=text_only`).then((res) => {
            if (!res.ok) throw new Error('Failed to fetch sefaria resource.');
            return res.json();
        }).then((data) => {
            if (data.error) throw new Error(data.error);
            setRelatedText(data.versions[0].text);
        }).catch((err) => {
            setSefariaRef('');
            setRelatedText('');
            setWarning(err.message);
        });
    };

    const handleDeleteRefFromList = (event, index) => {
        event.preventDefault();
        setSefariaRefChoices(prev => prev.filter((ref, i) => i !== index));
    };

    const submitSentance = (event) => {
        event.preventDefault();

        fetch('/editor/savesentance/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({
                page_id: idRef.current,
                sefaria_ref: sefariaRef,
                related_text: relatedText,
                boxes: highlightedBoxes,
                to_translate: toTranslate
            })
        }).then((response) => {
            if (!response.ok) throw new Error('Failed to upload');
            setExistingBoxes(prev => [...prev, ...highlightedBoxes]);
            setHilightedBoxes([]);
            setRelatedText('');
            setSefariaRefChoices(prev => prev.filter(ref => ref !== sefariaRef));
            setSefariaRef('');
            setToTranslate(false);
        }).catch((err) => {
            setWarning(err.message);
            console.error(err);
        });
    };

    const cancelSentance = (event) => {
        event.preventDefault();
        setSefariaRef('');
        setRelatedText('');
        setHilightedBoxes([]);
    };

    const submitPage = (event) => {
        event.preventDefault();
        fetch('/editor/completepage/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({
                page_id: idRef.current
            })
        }).then((res) => {
            return res.json();
        }).then((data) => {
            if (data.error) throw new Error(data.error);
            document.location.href = document.location.href;
        }).catch((err) => {
            setWarning(err.message);
            console.error(err);
        });
    };

    const handleCheckBox = (event) => {
        setToTranslate(event.target.checked);
    }

    return (
        <div className='refs-view'>
            {warning && <p style={{color: 'red'}}>{warning}</p>}
            {sefariaRef ? (
                <>
                    <h3>{sefariaRef}</h3>
                    <p>{relatedText}</p>
                    <input
                        type='checkbox'
                        checked={toTranslate}
                        onChange={handleCheckBox}
                    ></input>
                    <button onClick={submitSentance}>Submit</button>
                    <button onClick={cancelSentance}>Cancel</button>
                </>
            ) : (
                <>
                    {!sefariaRefChoices && <p>Loading Sefaria Refs...</p>}
                    {sefariaRefChoices && <p>Please, select sefaria item from the list</p>}
                    <ul>
                        {
                            sefariaRefChoices.map((choice, index) => (
                                <li key={index} className='ref-li'>
                                    <button onClick={(e) => handleSelectRef(e, index)} onContextMenu={(e) => handleDeleteRefFromList(e, index)}>
                                        {choice}
                                    </button>
                                </li>
                            ))
                        }
                    </ul>
                </>
            )
            }
            <button onClick={submitPage}>Complete this Page</button>
        </div>
    )

});

export default EditorRefsView;