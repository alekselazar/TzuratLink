import React, { useState, useEffect } from 'react';

const Test = () => {

    const [greeting, setGreeting] = useState('Hello World');

    const handleInput = (event) => {
        setGreeting(event.target.value);
    };
    
    return (
        <div>
            <h1>{greeting}</h1>
            <input value={greeting} onChange={handleInput}></input>
        </div>
    );
};

export default Test;