import ReactDOM from 'react-dom/client';
import React from 'react';
import EditorApp from './components/EditorApp';

const root = ReactDOM.createRoot(document.getElementById('loading'));

const app = React.createElement(EditorApp, { component: djangoComponent, props: djangoProps });

root.render(app);