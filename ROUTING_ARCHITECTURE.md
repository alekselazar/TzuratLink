# Routing Architecture: Hybrid Server/Client Routing

## Overview

This application uses **hybrid routing**:
- **Server-side routing** (Django): Handles initial page loads, direct URL access, and refreshes
- **Client-side routing** (React Router): Handles in-app navigation without full page reloads

## How It Works

### Scenario 1: Direct URL Access / Refresh
```
User types: http://localhost:8000/dafyomi/a
     ↓
Django URL routing matches: path('dafyomi/<str:amud>', views.daf_yomi)
     ↓
Django view renders template with SSR HTML
     ↓
Browser receives full HTML page
     ↓
React hydrates the existing HTML
```

### Scenario 2: In-App Navigation (Client-Side)
```
User clicks link in React app
     ↓
React Router intercepts the click
     ↓
React Router updates browser URL (history.pushState)
     ↓
React Router renders appropriate component
     ↓
No full page reload - instant navigation
```

## Implementation Flow

### Backend (Django)
1. **URL Patterns**: Define routes that Django handles
2. **Views**: Render templates with SSR data
3. **Catch-all route**: For any unmatched routes, serve the React app

### Frontend (React)
1. **React Router**: Handles client-side routing
2. **Link components**: Use `<Link>` instead of `<a>` for in-app navigation
3. **Route matching**: React Router matches URL and renders component
4. **Data fetching**: Fetch data via API when navigating client-side

## Key Components

### Django Side
- `reader/urls.py`: URL patterns
- `reader/views.py`: View functions that render templates
- Catch-all route: Serves React app for any unmatched routes

### React Side
- `BrowserRouter`: Wraps the app for client-side routing
- `Routes` & `Route`: Define route-to-component mappings
- `Link`: Client-side navigation links
- `useNavigate`: Programmatic navigation
- `useParams`: Access URL parameters

## Example Flow

### Initial Load
```
URL: /dafyomi/a
→ Django matches route
→ Django fetches data (with cache)
→ Django calls Node.js SSR server
→ Django renders template with SSR HTML
→ Browser displays page
→ React hydrates
```

### Client-Side Navigation
```
User clicks "Next Page" link
→ React Router intercepts
→ URL changes to /dafyomi/b (no page reload)
→ React Router renders PDFReader component
→ Component fetches data via /api/page/Berakhot:2b
→ Component updates with new data
```

## Benefits

1. **Fast initial load**: SSR provides immediate content
2. **Fast navigation**: Client-side routing is instant
3. **SEO friendly**: Search engines see full HTML
4. **Shareable URLs**: Each route has a unique URL
5. **Browser history**: Back/forward buttons work correctly
