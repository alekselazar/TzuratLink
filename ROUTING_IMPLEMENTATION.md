# Routing Implementation Guide

## How Routing Works

### 1. **Direct URL Access (Server-Side Routing)**

When a user types a URL or refreshes the page:

```
User visits: http://localhost:8000/dafyomi/a
     ↓
Django URL pattern matches: path('dafyomi/<str:amud>', views.daf_yomi)
     ↓
Django view:
  - Fetches data from MongoDB (with Redis cache)
  - Calls Node.js SSR server
  - Renders template with SSR HTML
     ↓
Browser receives full HTML with:
  - SSR-rendered React component
  - Navigation links (server-rendered)
  - Initial props in <script> tag
     ↓
React hydrates:
  - BrowserRouter initializes with current URL (/dafyomi/a)
  - React Router matches route and renders PDFReader
  - Navigation component replaces server-rendered nav
```

### 2. **In-App Navigation (Client-Side Routing)**

When a user clicks a link in the React app:

```
User clicks "Next Page" link
     ↓
React Router's <Link> component intercepts click
     ↓
Browser URL changes to: /dafyomi/b (via history.pushState)
     ↓
React Router matches new route: /dafyomi/:amud
     ↓
PDFReader component's useEffect detects route change:
  - params.amud changed from 'a' to 'b'
  - Fetches new data via /api/page/Berakhot:2b
     ↓
Component updates with new data
     ↓
No full page reload - instant navigation!
```

## Key Files

### Backend (Django)

**`reader/urls.py`**:
```python
urlpatterns = [
    path('dafyomi/', views.daf_yomi, name='daf yomi'),
    path('dafyomi/<str:amud>', views.daf_yomi, name='daf yomi'),
    re_path(r'^.*$', views.reader_catchall, name='reader_catchall'),  # Catch-all
]
```

**`reader/views.py`**:
- `daf_yomi()`: Handles `/dafyomi/:amud` routes, renders with SSR
- `reader_catchall()`: Handles any other routes, serves React app

### Frontend (React)

**`node/components/ReaderApp.js`**:
- Wraps app in `<BrowserRouter>`
- Defines routes using `<Routes>` and `<Route>`
- Passes initial props from SSR to components

**`node/components/Navigation.js`**:
- Uses `<Link>` for client-side navigation
- Reads current route from `useParams()`
- Updates URL without page reload

**`node/components/PDFReader.js`**:
- Uses `useParams()` to get route parameters
- Uses `useEffect` to detect route changes
- Fetches data when route changes client-side

## Usage Examples

### Creating Navigation Links

**❌ Wrong (causes full page reload):**
```jsx
<a href="/dafyomi/b">Next Page</a>
```

**✅ Correct (client-side navigation):**
```jsx
import { Link } from 'react-router-dom';

<Link to="/dafyomi/b">Next Page</Link>
```

### Programmatic Navigation

```jsx
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();
navigate('/dafyomi/b');  // Navigate programmatically
```

### Accessing Route Parameters

```jsx
import { useParams } from 'react-router-dom';

const { amud } = useParams();  // Gets 'a' or 'b' from /dafyomi/:amud
```

## Benefits

1. **Fast Initial Load**: SSR provides immediate content
2. **Fast Navigation**: Client-side routing is instant (no page reload)
3. **SEO Friendly**: Search engines see full HTML on initial load
4. **Shareable URLs**: Each route has a unique, shareable URL
5. **Browser History**: Back/forward buttons work correctly
6. **Smooth UX**: No white flash between page transitions

## Testing

1. **Direct URL**: Visit `http://localhost:8000/dafyomi/a` - should load with SSR
2. **Client Navigation**: Click "Next Page" - should navigate instantly without reload
3. **Browser Back**: Click browser back button - should work correctly
4. **Refresh**: Refresh on `/dafyomi/b` - should load with SSR
