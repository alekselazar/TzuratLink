import ReactDOM from 'react-dom/client';
import React from 'react';
import ReaderApp from './components/ReaderApp';

const appElement = document.getElementById('app');
const app = React.createElement(ReaderApp, { component: djangoComponent, props: djangoProps });

// Clear the server-rendered SEO fallback markup (if any) before mounting, so React
// takes over a clean container instead of reconciling against static HTML it didn't render.
appElement.innerHTML = '';
const root = ReactDOM.createRoot(appElement);
root.render(app);