import base64
import json
import urllib.request, urllib.error
import pytesseract
import fitz
from PIL import Image
from io import BytesIO
import threading
import time

from .models import Page

def convert_pdf(url):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        with urllib.request.urlopen(req) as res:
            pdf_bytes = res.read()

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        ocr_data = pytesseract.image_to_data(img, lang="heb",output_type="dict")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return b64, ocr_data
    except urllib.error.URLError as e:
        return None, None

def delete_page(page_id):
    try:
        page = Page.objects(id=page_id).first()
        if page:
            page.delete()
            return True
        return None
    except Exception as e:
        return None

def get_page(page_ref):
    try:
        page = Page.objects(ref=page_ref).first()
        return page
    except Exception as e:
        return None

def get_for_sref(sefaria_ref):
    """
    Get page data from MongoDB for a given Sefaria reference.
    Returns data formatted for React components.
    
    Args:
        sefaria_ref: Sefaria reference string (e.g., "Berakhot:2a")
    
    Returns:
        dict with keys: pageId, file, boxes, anchors
        Returns None if page not found
    """
    try:
        # Query MongoDB for page by ref
        page = Page.objects(ref=sefaria_ref).first()
        if not page:
            return None
        
        # Fetch PDF from source_pdf and convert to base64
        try:
            req = urllib.request.Request(page.source_pdf, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            with urllib.request.urlopen(req) as res:
                pdf_bytes = res.read()
            pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        except Exception as e:
            # If PDF fetch fails, return None
            return None
        
        # Convert bboxes to format expected by React (with sefaria_ref instead of ref)
        # Coordinates are floats in [0,1], convert to percent strings for CSS
        boxes = []
        for bbox in page.bboxes or []:
            boxes.append({
                "sefaria_ref": bbox.ref,
                "top": f"{float(bbox.top) * 100}%",
                "left": f"{float(bbox.left) * 100}%",
                "width": f"{float(bbox.width) * 100}%",
                "height": f"{float(bbox.height) * 100}%",
            })
        
        # Return data in format expected by React components
        return {
            "pageId": str(page.id),
            "file": pdf_base64,
            "boxes": boxes,
            "anchors": []  # Empty for now, can be populated if needed
        }
    except Exception as e:
        return None

def get_for_sref_with_timeout(sefaria_ref, timeout=2.0):
    """
    Get page data from MongoDB with a timeout for SSR/CSR decision.
    If data can be fetched within timeout, returns the data (SSR).
    If timeout is exceeded, returns {'timeout': True, 'ref': sefaria_ref} (CSR fallback).
    
    Args:
        sefaria_ref: Sefaria reference string (e.g., "Berakhot:2a")
        timeout: Maximum time in seconds to wait (default: 2.0)
    
    Returns:
        dict with page data if successful, or {'timeout': True, 'ref': sefaria_ref} if timeout
    """
    result = {'timeout': False, 'data': None}
    exception_occurred = [False]
    
    def fetch_data():
        try:
            data = get_for_sref(sefaria_ref)
            result['data'] = data
        except Exception as e:
            exception_occurred[0] = True
            result['data'] = None
    
    # Start fetching in a thread
    thread = threading.Thread(target=fetch_data)
    thread.daemon = True
    thread.start()
    thread.join(timeout=timeout)
    
    if thread.is_alive():
        # Timeout occurred
        return {'timeout': True, 'ref': sefaria_ref}
    
    if exception_occurred[0] or result['data'] is None:
        return None
    
    return result['data']