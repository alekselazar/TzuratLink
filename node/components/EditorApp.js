import React from 'react';
import PDFEditor from './PDFEditor';
import EditorInput from './EditorInput';
import PDFReviewer from './PDFReviewer';
import TranslationsEditor from './TranslationsEditor';
import '@react-pdf-viewer/core/lib/styles/index.css';

const EditorApp = ({ component, props }) => {

    const COMPONENTS = {
        'PDFEditor': PDFEditor,
        'EditorInput': EditorInput,
        'PDFReviewer': PDFReviewer,
        'TranslationsEditor': TranslationsEditor
    };

    const EditorParent = COMPONENTS[component];

    return (
        <EditorParent {...props} />
    )
};

export default EditorApp;