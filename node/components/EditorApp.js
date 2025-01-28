import React, { useState } from 'react';
import PDFEditor from './PDFEditor';
import EditorInput from './EditorInput';
import PDFReviewer from './PDFReviewer';
import '@react-pdf-viewer/core/lib/styles/index.css';
import '../../static/css/editor.css';

const EditorApp = ({ component, props }) => {

    const COMPONENTS = {
        'PDFEditor': PDFEditor,
        'EditorInput': EditorInput,
        'PDFReviewer': PDFReviewer
    };

    const EditorParent = COMPONENTS[component];

    return (
        <EditorParent {...props} />
    )
};

export default EditorApp;