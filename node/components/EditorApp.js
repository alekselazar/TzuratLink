import React from 'react';
import PageEditor from './PageEditor';
import EditorInput from './EditorInput';
import PDFReviewer from './PDFReviewer';
import TranslationsEditor from './TranslationsEditor';

const EditorApp = ({ component, props }) => {

    const COMPONENTS = {
        'PageEditor': PageEditor,
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