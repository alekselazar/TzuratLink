import React from 'react';

const PageTitle = ({ pageRef, hebrewTitle, lang = 'he' }) => {
    const isEnglish = lang === 'en';
    const title = isEnglish ? pageRef : (hebrewTitle || pageRef);

    return (
        <div
            style={{
                padding: '20px',
                borderBottom: '1px solid #e0e0e0',
                textAlign: isEnglish ? 'left' : 'right',
                fontSize: '24px',
                fontWeight: 'bold',
                backgroundColor: '#f8f9fa'
            }}
        >
            {title}
        </div>
    );
};

export default PageTitle;
