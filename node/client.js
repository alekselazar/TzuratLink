import ReactDOM from 'react-dom/client';
import React from 'react';
import ReaderApp from './components/ReaderApp';

const appElement = document.getElementById('app');

const app = React.createElement(ReaderApp, { 
    component: djangoComponent, 
    props: djangoProps,
    pageRef: typeof pageRef !== 'undefined' ? pageRef : null,
    initialLanguage: typeof pageLanguage !== 'undefined' ? pageLanguage : 'he'
});

// Client-side render (CSR-first approach for best performance)
const root = ReactDOM.createRoot(appElement);
root.render(app);