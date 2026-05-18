import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { SEDARIM } from './TalmudData';

const ALL_TRACTATES = SEDARIM.flatMap(s => s.tractates);
const MID = Math.ceil(ALL_TRACTATES.length / 2);

const Book = ({ tractate, available, navigate }) => (
    <div
        className={`book ${available ? 'book-available' : 'book-unavailable'}`}
        onClick={() => available && navigate(`/tractate/${encodeURIComponent(tractate.en)}`)}
        title={tractate.en}
        style={{ cursor: available ? 'pointer' : 'default' }}
    >
        <span className="book-title-he">{tractate.he}</span>
    </div>
);

const Bookshelf = ({ tractates, available, navigate }) => (
    <div className="home-bookshelf">
        {tractates.map(t => (
            <Book key={t.en} tractate={t} available={available.includes(t.en)} navigate={navigate} />
        ))}
    </div>
);

const LibraryHome = ({ lang = 'he' }) => {
    const [available, setAvailable] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const isHe = lang !== 'en';

    useEffect(() => {
        fetch('/api/library')
            .then(r => r.json())
            .then(data => { setAvailable(data.available || []); setLoading(false); })
            .catch(() => setLoading(false));
        document.body.classList.add('library-page');
        return () => document.body.classList.remove('library-page');
    }, []);

    return (
        <div className="library-home">
            <div className="library-pane">
                <div className="library-heading-wrap">
                    <h2 className="library-heading">תלמוד בבלי</h2>
                    <p className="library-subheading">Babylonian Talmud</p>
                </div>
                {loading ? (
                    <div className="pdf-loading"><div className="pdf-spinner" /></div>
                ) : (
                    <>
                        <Bookshelf tractates={ALL_TRACTATES.slice(0, MID)} available={available} navigate={navigate} />
                        <Bookshelf tractates={ALL_TRACTATES.slice(MID)} available={available} navigate={navigate} />
                    </>
                )}
            </div>
            <div className="library-promo">
                <p className="promo-text" dir={isHe ? 'rtl' : 'ltr'}>
                    {isHe
                        ? 'צורתלינק מחבר מסורת לטכנולוגיה. תהנו מצורת הדף המסורתית של ש"ס לצד משאבי ספריית ספריא'
                        : 'TzuratLink bridges tradition and technology. Enjoy both traditional Tzurat HaDaf layout and Sefaria library resources'}
                </p>
                <button
                    className="dafyomi-btn"
                    onClick={() => { window.location.href = '/dafyomi/'; }}
                >
                    {isHe ? 'קח אותי לדף היומי' : 'Take me to Daf HaYomi'}
                </button>
            </div>
        </div>
    );
};

export default LibraryHome;
