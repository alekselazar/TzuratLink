import React, { useState, useEffect } from "react";
import { useReaderState } from "./ReaderContext";

const AccordionItem = ({title, links}) => {
    const [isOpen, setIsOpen] = useState(false);
    const lang = useReaderState((ctx) => ctx.lang);
    return (
        <div className='accordion-item'>
            <div className="accordion-title" onClick={() => setIsOpen(!isOpen)}>{title + ' (' + links.length + ')'}</div>
            {links.map((link, idx) => (
                        <div key={idx} className="accordion-panel" style={{ transition: '0.4s', display: isOpen ? 'block' : 'none' }}>
                            <h5>{link.sourceRef}</h5>
                            <p dangerouslySetInnerHTML={{ __html: link.text }}></p>
                            <a className="sefara-link" href={`https://www.sefaria.org/${link.ref}?lang=he&with=all&lang2=he`} target="_blank">{lang.current.startsWith('en') ? 'Read on Sefaria' : 'עיין בספריא'}</a>
                        </div>
                    ))
                }
        </div>
    );
};

const ReaderRefsPanel = () => {

    const sefariaRef = useReaderState((ctx) => ctx.sefariaRef);
    const [title, setTitle] = useState('');
    const [mainCategory, setMainCategory] = useState('');
    const [text, setText] = useState('');
    const [links, setLinks] = useState({});
    const lang = useReaderState((ctx) => ctx.lang);
    const CATEGORIES = ['Commentary', 'Talmud', 'Mishnah', 'Halakhah', 'Tanakh'];
    const HE_CATEGORIES = ['מפרשים', 'תלמוד', 'משנה', 'הלכה', 'תנ"ך'];
    useEffect(() => {
        setText('');
        setLinks({});
        const fetchAllResources = async () => {
            const newLinks = {};
            const textRes = await fetch(`https://www.sefaria.org/api/v3/texts/${sefariaRef}?return_format=text_only`);
            if (!textRes.ok) {
                throw Error('Failed to fetch');
            }
            const textData = await textRes.json();
            if (textData.error) {
                throw Error(textData.error);
            }
            setTitle(lang.current.startsWith('en') ? textData.ref : textData.heRef);
            setMainCategory(textData.primary_category);
            setText(textData.versions[0].text);
            const refsRes = await fetch(`https://www.sefaria.org/api/links/${sefariaRef}`);
            if (!refsRes.ok) {
                throw Error('Failed to fetch links');
            }
            const refsData = await refsRes.json();
            if (refsData.error) {
                throw Error(refsData.error);
            }
            refsData.forEach(link => {
                const title = lang.current.startsWith('en') ? link.collectiveTitle.en : link.collectiveTitle.he;
                const text = link.he ? link.he : link.text;
                const sourceRef = lang.current.startsWith('en') ? link.sourceRef : link.sourceHeRef;
                if (!(CATEGORIES.includes(link.category))) {
                    return;
                }
                if (!newLinks[link.category]) {
                    newLinks[link.category] = {};
                }
                if (newLinks[link.category][title]) {
                    newLinks[link.category][title].push(
                        {
                            text: text,
                            ref: link.sourceRef,
                            sourceRef: sourceRef
                        }
                    );
                } else {
                    newLinks[link.category][title] = [
                        {
                            text: text,
                            ref: link.sourceRef,
                            sourceRef: sourceRef
                        }
                    ];
                }
            });
            setLinks(newLinks);
        }
        if (sefariaRef) {
            fetchAllResources().catch(err => {
                console.error('Error fetching resources:', err);
            });
        }
    }, [sefariaRef, lang]);

    return (
        <div className="refs-panel">
            {text ? (
                <div className="related-text" style={{ borderTop: `5px solid var(--${mainCategory.toLocaleLowerCase()})`}}>
                    <h5>{title}</h5>
                    <p>{text}</p>
                    <a className="sefara-link" href={`https://www.sefaria.org.il/${sefariaRef}`} target="_blank">{lang.current.startsWith('en') ? 'Read on Sefaria' : 'עיין בספריא'}</a>
                </div>
            ) : (
                <div className="related-text">
                    <span>{lang.current.startsWith('en') ? 'Loading...' : 'טעינה...'}</span>
                </div>
            )   
            }
            <div className="accordion">
            {
                Object.keys(links).map((category, i) => (
                    <div key={category} className="category" style={{ borderTop: `5px solid var(--${category.toLocaleLowerCase()})` }}>
                        <div className="category-name">{lang.current.startsWith('en') ? category : HE_CATEGORIES[CATEGORIES.indexOf(category)]}</div>
                        {
                            Object.keys(links[category]).map((ref) => (
                                <AccordionItem key={ref} title={ref} links={links[category][ref]} />
                            ))
                        }
                    </div>
                )
            )
            }
            </div>
        </div>
    )
};

export default ReaderRefsPanel;