# Cache Warming & Pre-rendering Guide

This guide explains how to use TzuratLink's pre-rendering and cache warming system to optimize performance.

## Overview

Pre-rendering caches page data and metadata before users request them. This results in:
- **Instant page loads** for pre-rendered pages
- **Reduced database load** from repeated requests
- **Better SEO** with pre-generated metadata
- **Improved user experience** for popular pages

## Quick Start

### Pre-render Today's Daf Yomi
```bash
python manage.py prerender_pages --daf-yomi
```

### Pre-render a Specific Page
```bash
python manage.py prerender_pages --ref "Berakhot:2a"
```

### Pre-render All Pages
```bash
python manage.py prerender_pages --all
```

### Pre-render with Custom Cache Duration
```bash
# Cache for 7 days (604800 seconds)
python manage.py prerender_pages --daf-yomi --duration 604800

# Cache for 1 hour (3600 seconds)
python manage.py prerender_pages --all --duration 3600
```

### Pre-render with Limit
```bash
# Pre-render first 100 pages
python manage.py prerender_pages --all --limit 100
```

## Automatic Pre-rendering on Startup

Add this to `tzuratlink/settings.py`:

```python
# Pre-render Daf Yomi pages on app startup
PRERENDER_ON_STARTUP = True
```

This will automatically cache today's Daf Yomi pages when Django starts up.

## Management Command API

```bash
python manage.py prerender_pages [OPTIONS]
```

### Options
- `--daf-yomi` — Pre-render today's Daf Yomi (amud a and b)
- `--all` — Pre-render all available pages
- `--limit N` — Limit to N pages (use with `--all`)
- `--ref REFERENCE` — Pre-render specific page (e.g., "Berakhot:2a")
- `--duration SECONDS` — Cache duration (default: 86400 = 24 hours)

## Python API

You can also use the pre-rendering functions programmatically:

### Pre-render Daf Yomi
```python
from core.utils import prerender_daf_yomi

# Pre-render with 24-hour cache
results = prerender_daf_yomi(cache_duration=86400)

for ref, (success, message) in results.items():
    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")
```

### Pre-render Specific Page
```python
from core.utils import prerender_page

success, message = prerender_page("Berakhot:2a", cache_duration=86400)
if success:
    print(message)
else:
    print(f"Error: {message}")
```

### Pre-render All Pages
```python
from core.utils import prerender_all_pages

# Pre-render all pages, limit to 1000
results = prerender_all_pages(cache_duration=604800, limit=1000)
```

### Get All Available Pages
```python
from core.utils import get_all_available_pages

pages = get_all_available_pages()
print(f"Total pages available: {len(pages)}")
```

## Performance Benefits

### Without Pre-rendering
```
User visits /dafyomi/a
→ Django queries MongoDB (~200-500ms)
→ Django generates metadata (~50ms)
→ Browser loads React bundle (~50-200ms)
→ React mounts and initializes (~100-300ms)
Total: 400-1000ms
```

### With Pre-rendering
```
User visits /dafyomi/a
→ Django gets data from cache (~5-10ms)
→ Django gets metadata from cache (~5-10ms)
→ Browser loads React bundle (~50-200ms)
→ React mounts with cached data (~50-100ms)
Total: 110-320ms (3-8x faster!)
```

## Best Practices

### For High-Traffic Sites
1. **Pre-render daily at midnight:**
   ```bash
   # Add to crontab
   0 0 * * * /path/to/manage.py prerender_pages --daf-yomi
   ```

2. **Enable startup pre-rendering:**
   ```python
   # tzuratlink/settings.py
   PRERENDER_ON_STARTUP = True
   ```

3. **Use long cache duration:**
   ```bash
   python manage.py prerender_pages --daf-yomi --duration 604800
   ```

### For Development
1. **Reduce cache duration:**
   ```bash
   python manage.py prerender_pages --daf-yomi --duration 3600
   ```

2. **Don't enable startup pre-rendering:**
   ```python
   # tzuratlink/settings.py
   PRERENDER_ON_STARTUP = False
   ```

## Cache Invalidation

Cache is automatically invalidated when:
- A page is saved in MongoDB
- A page is deleted
- Manual cache clear

To manually clear cache:
```python
from django.core.cache import cache
cache.clear()  # Clear all cache
```

To clear specific page cache:
```python
from django.core.cache import cache
cache.delete('page_data:Berakhot:2a')
cache.delete('page_meta:Berakhot:2a')
```

## Monitoring Cache Hit Rate

Check Redis cache stats:
```bash
redis-cli INFO stats
```

Look for `keyspace_hits` and `keyspace_misses` to calculate hit rate:
```
hit_rate = keyspace_hits / (keyspace_hits + keyspace_misses)
```

Goal: >80% cache hit rate for optimal performance.

## Troubleshooting

### Pre-rendering fails with "Page not found"
- Ensure the page exists in MongoDB
- Check the page reference format (should be "Berakhot:2a", not "Berakhot 2a")

### Pre-rendering is slow
- Too many pages at once — use `--limit` to batch
- MongoDB is slow — check database performance
- Cache is full — clear old cache entries

### Daf Yomi pre-render fails
- Check internet connection (fetches from Sefaria API)
- Sefaria API might be down
- Try manually with: `python manage.py prerender_pages --ref "Berakhot:2a"`

## See Also
- [DEPLOYMENT.md](DEPLOYMENT.md) — Deployment configuration
- [ROUTING_ARCHITECTURE.md](ROUTING_ARCHITECTURE.md) — Routing overview
