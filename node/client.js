import ReactDOM from 'react-dom/client';
import React from 'react';
import EditorApp from './components/EditorApp';
import ReaderApp from './components/ReaderApp';

const appElement = document.getElementById('app');
const hasSSR = appElement.children.length > 0 && !appElement.querySelector('h1');

const App = djangoApp === 'EditorApp' ? EditorApp : ReaderApp;

const app = React.createElement(App, { component: djangoComponent, props: djangoProps });

if (hasSSR) {
    // Hydrate existing SSR HTML
    const root = ReactDOM.hydrateRoot(appElement, app);
} else {
    // Client-side render (CSR)
    const root = ReactDOM.createRoot(appElement);
    root.render(app);
}