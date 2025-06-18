import React from 'react';
import PageEditor from './PageEditor';
import PageReviewer from './PageReviewer';
import EditorInput from './EditorInput';
import TranslationsEditor from './TranslationsEditor';

const EditorApp = ({ component, props }) => {

    const COMPONENTS = {
        'PageEditor': PageEditor,
        'EditorInput': EditorInput,
        'PageReviewer': PageReviewer,
        'TranslationsEditor': TranslationsEditor
    };

    const EditorParent = COMPONENTS[component];

    return (
        <EditorParent {...props} />
    )
};

export default EditorApp;