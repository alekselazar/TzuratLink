import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Navigation = ({ pageRef, lang = 'he' }) => {
    const navigate = useNavigate();
    const [nextPage, setNextPage] = useState(null);
    const [prevPage, setPrevPage] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!pageRef) return;

        const fetchNavigation = async () => {
            try {
                // Fetch next page
                const nextRes = await fetch(`/api/dafyomi/next/${pageRef}`);
                if (nextRes.ok) {
                    const nextData = await nextRes.json();
                    if (nextData.exists) {
                        setNextPage(nextData.ref);
                    }
                }

                // Fetch previous page
                const prevRes = await fetch(`/api/dafyomi/prev/${pageRef}`);
                if (prevRes.ok) {
                    const prevData = await prevRes.json();
                    if (prevData.exists) {
                        setPrevPage(prevData.ref);
                    }
                }
            } catch (error) {
                console.error('Error fetching navigation:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchNavigation();
    }, [pageRef]);

    const isEnglish = lang === 'en';

    if (loading) return null;

    const buttonStyle = {
        padding: '10px 15px',
        margin: '0 5px',
        fontSize: '18px',
        backgroundColor: '#007bff',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
        transition: 'background-color 0.3s'
    };

    const navContainerStyle = {
        display: 'flex',
        flexDirection: isEnglish ? 'row' : 'row-reverse',
        justifyContent: 'flex-start',
        alignItems: 'center',
        gap: '10px',
        padding: '10px 20px'
    };

    return (
        <nav id="main-nav" style={navContainerStyle}>
            {prevPage && (
                <button 
                    id="navigate-prev"
                    onClick={() => navigate(`/page/${prevPage}`)}
                    onMouseEnter={(e) => e.target.style.backgroundColor = '#0056b3'}
                    onMouseLeave={(e) => e.target.style.backgroundColor = '#007bff'}
                    style={buttonStyle}
                    title={isEnglish ? 'Previous Page' : 'דף קודם'}
                >
                    {isEnglish ? '←' : '→'}
                </button>
            )}
            {nextPage && (
                <button 
                    id="navigate-next"
                    onClick={() => navigate(`/page/${nextPage}`)}
                    onMouseEnter={(e) => e.target.style.backgroundColor = '#0056b3'}
                    onMouseLeave={(e) => e.target.style.backgroundColor = '#007bff'}
                    style={buttonStyle}
                    title={isEnglish ? 'Next Page' : 'דף הבא'}
                >
                    {isEnglish ? '→' : '←'}
                </button>
            )}
        </nav>
    );
};

export default Navigation;
