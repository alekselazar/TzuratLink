import React, { useEffect, useState } from "react";
import PDFEditor from "./PDFEditor";
import PDFReviewer from "./PDFReviewer";
import TranslationsEditor from './TranslationsEditor';

const EditorTaskManager = ({ incompleted, unreviewed, untranslated }) => {

    const [ChosenComponent, setChosenComponent] = useState(null);
    const [props, setProps] = useState(null);

    const handleComponent = (event, componentName) => {
        event.preventDefault();

        const COMPONENTS = {
            'PDFEditor': PDFEditor,
            'PDFReviewer': PDFReviewer,
            'TranslationsEditor': TranslationsEditor
        };

        const PROPS = {
            'PDFEditor': incompleted,
            'PDFReviewer': unreviewed,
            'TranslationsEditor': untranslated
        };

        setChosenComponent(COMPONENTS[componentName]);
        setProps(PROPS[componentName]);

    };

    return (
        <>
            {
                ChosenComponent ? (
                    <ChosenComponent {...props}/>
                ) : (
                    <>
                        <h1>Here your tasks:</h1>
                        {incompleted && <><p>You have uncompleted page(s)</p><button onClick={(e)=>handleComponent(e, 'PDFEditor')}></button></>}
                        {unreviewed && <><p>You have unreviewed page(s)</p><button onClick={(e)=>handleComponent(e, 'PDFReviewer')}></button></>}
                        {untranslated && <><p>You have unedited translations</p><button onClick={(e)=>handleComponent(e, 'TranslationsEditor')}></button></>}
                    </>
                )
            }
        </>
    );
};

export default EditorTaskManager;