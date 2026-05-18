import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { findTractate } from './TalmudData';

const HE_VALS = [
    [400,'ת'],[300,'ש'],[200,'ר'],[100,'ק'],
    [90,'צ'],[80,'פ'],[70,'ע'],[60,'ס'],[50,'נ'],
    [40,'מ'],[30,'ל'],[20,'כ'],[10,'י'],
    [9,'ט'],[8,'ח'],[7,'ז'],[6,'ו'],[5,'ה'],
    [4,'ד'],[3,'ג'],[2,'ב'],[1,'א'],
];

function toHebrewNumeral(n) {
    let result = '', rem = n;
    for (const [val, ch] of HE_VALS) {
        while (rem >= val) { result += ch; rem -= val; }
    }
    return result.replace('יה', 'טו').replace('יו', 'טז');
}

const AmudCard = ({ pageRef, daf, side, navigate }) => (
    <button
        className="amud-card"
        onClick={() => navigate(`/page/${encodeURIComponent(pageRef)}`)}
        title={pageRef}
    >
        <span className="amud-he">{toHebrewNumeral(daf)}{side === 'a' ? '.' : ':'}</span>
        <span className="amud-latin">{daf}{side}</span>
    </button>
);

const TractateView = () => {
    const { name } = useParams();
    const navigate = useNavigate();
    const [amudim, setAmudim] = useState([]);
    const [loading, setLoading] = useState(true);

    const tractate = useMemo(() => findTractate(decodeURIComponent(name)), [name]);

    useEffect(() => {
        setLoading(true);
        fetch(`/api/tractate/${encodeURIComponent(decodeURIComponent(name))}`)
            .then(r => r.json())
            .then(data => { setAmudim(data.amudim || []); setLoading(false); })
            .catch(() => setLoading(false));
    }, [name]);

    return (
        <div className="tractate-page">
            <div className="tractate-nav">
                <button className="back-btn" onClick={() => navigate('/')}>
                    ← Library
                </button>
                {tractate.seder && (
                    <span className="tractate-breadcrumb">{tractate.sederEn} · {tractate.seder}</span>
                )}
            </div>

            <div className="tractate-header">
                <h2 className="tractate-he">{tractate.he}</h2>
                <p className="tractate-en">{tractate.en}</p>
            </div>

            {loading ? (
                <div className="pdf-loading">
                    <div className="pdf-spinner" />
                </div>
            ) : amudim.length === 0 ? (
                <div className="tractate-wip">
                    <div className="tractate-wip-icon">📖</div>
                    <h3 className="tractate-wip-title">We are working on this</h3>
                    <p className="tractate-wip-text">
                        {tractate.en} is not yet available on TzuratLink.<br />
                        Check back soon — we are adding new tractates regularly.
                    </p>
                </div>
            ) : (
                <>
                    <p className="tractate-count">{amudim.length} amudim available</p>
                    <div className="amud-grid">
                        {amudim.map(a => (
                            <AmudCard
                                key={a.ref}
                                pageRef={a.ref}
                                daf={a.daf}
                                side={a.side}
                                navigate={navigate}
                            />
                        ))}
                    </div>
                </>
            )}
        </div>
    );
};

export default TractateView;
