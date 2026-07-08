"""
core/render.py

Fetches a PDF from a URL, renders page 0 with PyMuPDF, applies the
optional CropBox (0-1 fractions of the full page), and returns PNG bytes.

Results are cached (Redis when configured, falls back to in-memory) for 24
hours so repeated requests don't re-download the PDF.
"""

import urllib.request
import fitz  # PyMuPDF
from django.core.cache import cache

DPI = 150  # render resolution — increase for sharper images at the cost of size


def render_page_png(page_doc) -> bytes:
    """
    Render page_doc to a cropped PNG.

    Args:
        page_doc: models.Page instance with source_pdf and optional crop_box.

    Returns:
        PNG bytes of the (optionally cropped) page image.
    """
    cache_key = f'render_png:{page_doc.id}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    req = urllib.request.Request(
        page_doc.source_pdf,
        headers={'User-Agent': 'TzuratLink/1.0'},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        pdf_bytes = resp.read()

    doc = fitz.open(stream=pdf_bytes, filetype='pdf')
    page = doc[0]
    full = page.rect  # fitz.Rect(x0, y0, x1, y1) in points

    if page_doc.crop_box:
        cb = page_doc.crop_box
        w = full.width
        h = full.height
        clip = fitz.Rect(
            full.x0 + cb.left * w,
            full.y0 + cb.top * h,
            full.x0 + cb.right * w,
            full.y0 + cb.bottom * h,
        )
    else:
        clip = full

    mat = fitz.Matrix(DPI / 72, DPI / 72)
    pix = page.get_pixmap(matrix=mat, clip=clip, alpha=False)
    png_bytes = pix.tobytes('png')
    doc.close()

    cache.set(cache_key, png_bytes, 86400)
    return png_bytes
