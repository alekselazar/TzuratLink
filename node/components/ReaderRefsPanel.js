import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useReaderState } from "./ReaderContext";


const TRACTATE_RE = /^(.+?)\s+\d+[ab]$/;

const CATEGORIES = ['Commentary', 'Talmud', 'Mishnah', 'Halakhah', 'Tanakh'];
const HE_CATEGORIES = ['מפרשים', 'תלמוד', 'משנה', 'הלכה', 'תנ"ך'];

const AccordionItem = ({ title, links }) => {
    const [isOpen, setIsOpen] = useState(false);
    const lang = useReaderState((ctx) => ctx.lang);

    return (
        <div className="accordion-item">
            <div className="accordion-title" onClick={() => setIsOpen(!isOpen)}>
                {title + ' (' + links.length + ')'}
            </div>
            {links.map((link, idx) => (
                <div
                    key={idx}
                    className="accordion-panel"
                    style={{ display: isOpen ? 'block' : 'none' }}
                >
                    <h5 dir={link.isHebrew ? 'rtl' : 'ltr'}>{link.sourceRef}</h5>
                    <p
                        dir={link.isHebrew ? 'rtl' : 'ltr'}
                        dangerouslySetInnerHTML={{ __html: link.text }}
                    />
                    <a
                        className="sefara-link"
                        href={`https://www.sefaria.org/${link.ref}?lang=he&with=all&lang2=he`}
                        target="_blank"
                        rel="noreferrer"
                    >
                        {lang.current.startsWith('en') ? 'Read on Sefaria' : 'עיין בספריא'}
                    </a>
                </div>
            ))}
        </div>
    );
};

const ReaderRefsPanel = () => {
    const pageRef = useReaderState((ctx) => ctx.pageRef);
    const sefariaRef = useReaderState((ctx) => ctx.sefariaRef);
    const setSefariaRef = useReaderState((ctx) => ctx.setSefariaRef);
    const lang = useReaderState((ctx) => ctx.lang);
    const navigate = useNavigate();

    const goToTractate = () => {
        const m = pageRef && TRACTATE_RE.exec(decodeURIComponent(pageRef));
        if (m) navigate(`/tractate/${encodeURIComponent(m[1])}`);
    };

    const [title, setTitle] = useState('');
    const [mainCategory, setMainCategory] = useState('');
    const [text, setText] = useState('');
    const [textLang, setTextLang] = useState('he');
    const [links, setLinks] = useState({});

    useEffect(() => {
        if (!sefariaRef) return;
        setTitle('');
        setText('');
        setLinks({});

        const fetchAll = async () => {
            const textRes = await fetch(
                `https://www.sefaria.org/api/v3/texts/${sefariaRef}?return_format=text_only`
            );
            if (!textRes.ok) throw new Error('Failed to fetch text');
            const textData = await textRes.json();
            if (textData.error) throw new Error(textData.error);

            const version = textData.versions?.[0];
            const versionLang = version?.language ?? 'he';

            setTitle(lang.current.startsWith('en') ? (textData.ref || sefariaRef) : (textData.heRef || sefariaRef));
            setMainCategory(textData.primary_category);
            setText(version?.text ?? '');
            setTextLang(versionLang);

            const refsRes = await fetch(`https://www.sefaria.org/api/links/${sefariaRef}`);
            if (!refsRes.ok) throw new Error('Failed to fetch links');
            const refsData = await refsRes.json();
            if (refsData.error) throw new Error(refsData.error);

            const newLinks = {};
            refsData.forEach(link => {
                if (!CATEGORIES.includes(link.category)) return;
                const isHebrew = Boolean(link.he);
                const linkText = isHebrew ? link.he : link.text;
                const title = lang.current.startsWith('en')
                    ? link.collectiveTitle.en
                    : link.collectiveTitle.he;
                const sourceRef = lang.current.startsWith('en')
                    ? link.sourceRef
                    : link.sourceHeRef;
                if (!newLinks[link.category]) newLinks[link.category] = {};
                const entry = { text: linkText, ref: link.sourceRef, sourceRef, isHebrew };
                if (newLinks[link.category][title]) {
                    newLinks[link.category][title].push(entry);
                } else {
                    newLinks[link.category][title] = [entry];
                }
            });
            setLinks(newLinks);
        };

        fetchAll().catch(err => console.error('ReaderRefsPanel fetch error:', err));
    }, [sefariaRef, lang]);

    return (
        <div className="refs-panel">
            <div className="refs-panel-header">
                <span
                    className="refs-panel-title refs-panel-title--link"
                    onClick={goToTractate}
                    role="button"
                    dir={textLang === 'he' ? 'rtl' : 'ltr'}
                >
                    {title || sefariaRef}
                </span>
                <button
                    className="refs-close-btn"
                    onClick={() => setSefariaRef('')}
                    title="Close"
                >
                    ×
                </button>
            </div>

            <div className="refs-panel-body">
                {text ? (
                    <div
                        className="related-text"
                        style={{ borderTop: `5px solid var(--${mainCategory.toLowerCase()})` }}
                    >
                        <p dir={textLang === 'he' ? 'rtl' : 'ltr'}>{text}</p>
                        <a
                            className="sefara-link"
                            href={`https://www.sefaria.org.il/${sefariaRef}`}
                            target="_blank"
                            rel="noreferrer"
                        >
                            {lang.current.startsWith('en') ? 'Read on Sefaria' : 'עיין בספריא'}
                        </a>
                    </div>
                ) : (
                    <div className="pdf-loading">
                        <div className="pdf-spinner refs-spinner" />
                    </div>
                )}

                <div className="accordion">
                    {Object.keys(links).map(category => (
                        <div
                            key={category}
                            className="category"
                            style={{ borderTop: `5px solid var(--${category.toLowerCase()})` }}
                        >
                            <div className="category-name">
                                {lang.current.startsWith('en')
                                    ? category
                                    : HE_CATEGORIES[CATEGORIES.indexOf(category)]}
                            </div>
                            {Object.keys(links[category]).map(ref => (
                                <AccordionItem key={ref} title={ref} links={links[category][ref]} />
                            ))}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ReaderRefsPanel;
