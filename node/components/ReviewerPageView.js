import React, { useRef } from 'react';
import ReviewerBoxesLayer from './ReviewerBoxesLayer';
import { useReviewerState } from './ReviewerContext';


const ReviewedPageView = React.memo(() => {

    const fileBlobUrl = useRef(useReviewerState((ctx) => ctx.fileBlobUrl));
    
    return (
        <div>
            <img src={fileBlobUrl} style={{ width: '100%' }}></img>
            <ReviewerBoxesLayer/>
        </div>
    )

});

export default ReviewedPageView;