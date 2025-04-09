import ReactDOM from 'react-dom/client';
import React from 'react';
import EditorApp from './components/EditorApp';
import ReaderApp from './components/ReaderApp';

const root = ReactDOM.createRoot(document.getElementById('app'));

const App = djangoApp === 'Editor' ? EditorApp : ReaderApp

const app = React.createElement(App, { component: djangoComponent, props: djangoProps });

root.render(app);