import { useState, useEffect } from "react";
import { useReaderState } from "./ReaderContext";

const textDir = (lang) => lang === 'he' ? 'rtl' : 'ltr';

const AccordionItem = ({ title, links }) => {
    const [isOpen, setIsOpen] = useState(false);
    const lang = useReaderState((ctx) => ctx.lang);
    return (
        <div className='accordion-item'>
            <div className="accordion-title" onClick={() => setIsOpen(!isOpen)}>{title + ' (' + links.length + ')'}</div>
            {links.map((link, idx) => (
                <div key={idx} className="accordion-panel" style={{ transition: '0.4s', display: isOpen ? 'block' : 'none' }}>
                    <h5 dir={textDir(link.textLang)}>{link.sourceRef}</h5>
                    <p dir={textDir(link.textLang)} dangerouslySetInnerHTML={{ __html: link.text }}></p>
                    <a className="sefara-link" href={`https://www.sefaria.org/${link.ref}?lang=he&with=all&lang2=he`} target="_blank">
                        {lang.current.startsWith('en') ? 'Read on Sefaria' : 'עיין בספריא'}
                    </a>
                </div>
            ))}
        </div>
    );
};

const ReaderRefsPanel = () => {

    const sefariaRef = useReaderState((ctx) => ctx.sefariaRef);
    const [title, setTitle] = useState('');
    const [titleLang, setTitleLang] = useState('he');
    const [mainCategory, setMainCategory] = useState('');
    const [text, setText] = useState('');
    const [textLang, setTextLang] = useState('he');
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
            if (!textRes.ok) throw Error('Failed to fetch');
            const textData = await textRes.json();
            if (textData.error) throw Error(textData.error);

            const isEnglish = lang.current.startsWith('en');
            setTitle(isEnglish ? textData.ref : textData.heRef);
            setTitleLang(isEnglish ? 'en' : 'he');
            setMainCategory(textData.primary_category);

            // versions[0].language tells us whether the text is 'he' or 'en'
            const version = textData.versions[0];
            setText(version.text);
            setTextLang(version.language || 'he');

            const refsRes = await fetch(`https://www.sefaria.org/api/links/${sefariaRef}`);
            if (!refsRes.ok) throw Error('Failed to fetch links');
            const refsData = await refsRes.json();
            if (refsData.error) throw Error(refsData.error);

            refsData.forEach(link => {
                if (!CATEGORIES.includes(link.category)) return;
                const title = isEnglish ? link.collectiveTitle.en : link.collectiveTitle.he;
                // Prefer Hebrew text; track which language was chosen
                const hasHebrew = !!link.he;
                const text = hasHebrew ? link.he : link.text;
                const linkTextLang = hasHebrew ? 'he' : 'en';
                const sourceRef = isEnglish ? link.sourceRef : link.sourceHeRef;

                if (!newLinks[link.category]) newLinks[link.category] = {};
                if (!newLinks[link.category][title]) newLinks[link.category][title] = [];
                newLinks[link.category][title].push({ text, textLang: linkTextLang, ref: link.sourceRef, sourceRef });
            });
            setLinks(newLinks);
        };
        if (sefariaRef) {
            fetchAllResources().catch(err => console.error('Error fetching resources:', err));
        }
    }, [sefariaRef, lang]);

    return (
        <div className="refs-panel">
            {text ? (
                <div className="related-text" style={{ borderTop: `5px solid var(--${mainCategory.toLocaleLowerCase()})` }}>
                    <h5 dir={textDir(titleLang)}>{title}</h5>
                    <p dir={textDir(textLang)}>{text}</p>
                    <a className="sefara-link" href={`https://www.sefaria.org.il/${sefariaRef}`} target="_blank">
                        {lang.current.startsWith('en') ? 'Read on Sefaria' : 'עיין בספריא'}
                    </a>
                </div>
            ) : (
                <div className="related-text">
                    <span>{lang.current.startsWith('en') ? 'Loading...' : 'טעינה...'}</span>
                </div>
            )}
            <div className="accordion">
                {Object.keys(links).map((category) => (
                    <div key={category} className="category" style={{ borderTop: `5px solid var(--${category.toLocaleLowerCase()})` }}>
                        <div className="category-name">
                            {lang.current.startsWith('en') ? category : HE_CATEGORIES[CATEGORIES.indexOf(category)]}
                        </div>
                        {Object.keys(links[category]).map((ref) => (
                            <AccordionItem key={ref} title={ref} links={links[category][ref]} />
                        ))}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ReaderRefsPanel;
