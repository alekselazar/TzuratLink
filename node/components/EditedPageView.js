import React, { useRef } from 'react';
import EditorBoxesLayer from './EditorBoxesLayer';
import EditedLayer from './EditedLayer';
import EditorLinesLayer from './EditorLinesLayer';
import { usePageEditorState } from './PageEditorContext';


const EditedPageView = React.memo(() => {

    const fileBlobUrl = useRef(usePageEditorState((ctx) => ctx.fileBlobUrl));
    
    return (
        <div>
            <img src={fileBlobUrl} style={{ width: '100%' }}></img>
            <EditedLayer/>
            <EditorBoxesLayer/>
            <EditorLinesLayer/>
        </div>
    )

});

export default EditedPageView;