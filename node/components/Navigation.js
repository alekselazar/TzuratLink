import React from 'react';
import { Link, useParams } from 'react-router-dom';

const Navigation = () => {
    const params = useParams();
    const currentAmud = params.amud || 'a';
    
    return (
        <nav>
            {currentAmud === 'a' && (
                <Link to="/dafyomi/b" id="navigate">Next Page</Link>
            )}
            {currentAmud === 'b' && (
                <Link to="/dafyomi/a" id="navigate">Previous Page</Link>
            )}
        </nav>
    );
};

export default Navigation;
