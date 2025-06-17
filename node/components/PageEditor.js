import React from 'react';
import { PageStateProvider } from './PageEditorContext';
import EditedPageView from './EditedPageView';
import EditorRefsView from './EditorRefsView';

const PageEditor = (props) => {

    return (
        <PageStateProvider {...props}>
            <div style={{ display: 'flex', width: '100%' }}>
                <div style={{ width: '75%', position: 'relative' }}>
                    <EditedPageView />
                </div>
                <div style={{ width: '25%', padding: '20px' }}>
                    <EditorRefsView />                    
                </div>
            </div>
        </PageStateProvider>
    );
};

export default PageEditor;