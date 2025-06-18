import React from 'react';
import { ReviewStateProvider, useReviewerState } from './ReviewerContext';
import ReviewerPageView from './ReviewerPageView';

const PageReviewer = (props) => {

    const sefariaRef = useReviewerState((ctx) => ctx.sefariaRef);

    return (
        <ReviewStateProvider {...props}>
            <div style={{ display: 'flex', width: '100%' }}>
                <div style={{ width: '75%', position: 'relative' }}>
                    <ReviewerPageView />
                </div>
                <div style={{ width: '25%', padding: '20px' }}>
                    {
                        sefariaRef ? (
                            <p>{sefariaRef}</p>
                        ) : (
                            <p>Choose sentance from daf</p>
                        )
                    }                    
                </div>
            </div>
        </ReviewStateProvider>
    );
};

export default PageReviewer;