import base64
import json
import urllib.request, urllib.error
import pytesseract
import fitz
from PIL import Image
from io import BytesIO

from .models import Page, BoundingContainer, TranslatedSentance, Translation, PageAnchor

def get_incompleted_page():
    try:
        incompleted = Page.objects.filter(completed=False).first()
        return get_page_data(incompleted)
    except Page.DoesNotExist as e:
        return None

def get_unreviewed_page():
    try:    
        unreviewed = Page.objects.filter(reviewed=False).first()
        return get_page_data(unreviewed)
    except Page.DoesNotExist as e:
        return None

def get_page_data(page):
    try:
        page_dict = {
            'pageId': page.pk,
            'file': page.file,
            'boxes': [],
            'anchors': []
        }
        try:
            b_containers = BoundingContainer.objects.filter(page_ref=page)
            for container in b_containers:
                page_dict['boxes'].append({
                    'top': container.top,
                    'left': container.left,
                    'width': container.width,
                    'height': container.height,
                    'sefaria_ref' : container.sefaria_ref
                })
        except BoundingContainer.DoesNotExist as e:
            pass
        try:
            page_anchors = PageAnchor.objects.filter(page=page)
            for anchor in page_anchors:
                page_dict['anchors'].append(anchor.sefaria_ref)
        except PageAnchor.DoesNotExist as e:
            pass
        return page_dict
    except:
        return None
    
def create_new_page(url, anchors):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        with urllib.request.urlopen(req) as res:
            pdf_bytes = res.read()

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("L", [pix.width, pix.height], pix.samples)
        ocr_data = pytesseract.image_to_data(img, lang="heb+rashi",output_type="dict")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        page = Page(
            file=b64,
            foreign_url=url,
            reviewed=False,
            completed=False,
            ocr=json.dumps(ocr_data, ensure_ascii=False)
        )
        page.save()
        for anchor in anchors:
            pageanchor = PageAnchor(page=page, sefaria_ref=anchor)
            pageanchor.save()
        return page
    except urllib.error.URLError as e:
        return None

def delete_page(page_id):
    try:
        page = Page.objects.get(pk=page_id)
        return page.delete()
    except Page.DoesNotExist as e:
        return None
    
def cleanup_page(page_id):
    try:
        page = Page.objects.get(pk=page_id)
        try:
            b_containers = BoundingContainer.objects.filter(page_ref=page)
            for container in b_containers:
                container.delete()
        except BoundingContainer.DoesNotExist as e:
            pass
        page.completed = False
        page.reviewed = False
        page.save()
        return page.pk
    except Page.DoesNotExist as e:
        return None
    
def complete(page_id):
    try:
        page = Page.objects.get(pk=page_id)
        page.completed = True
        page.save()
        return page.pk
    except Page.DoesNotExist as e:
        return None
    
def review(page_id):
    try:
        page = Page.objects.get(pk=page_id)
        page.reviewed = True
        page.save()
        return page.pk
    except Page.DoesNotExist as e:
        return None
    
def save_sent(page_id, sefaria_ref, text, boxes, to_translate):
    try:
        page = Page.objects.get(pk=page_id)
        for box in boxes:
            b_container = BoundingContainer(
                sefaria_ref=sefaria_ref,
                top=box['top'],
                left=box['left'],
                width=box['width'],
                height=box['height'],
                page_ref=page
            )
            b_container.save()
        if to_translate:
            sentance = TranslatedSentance(sentance=text, sefaria_ref=sefaria_ref)
            sentance.save()
            return sentance.pk
        else:
            return page.pk
    except Page.DoesNotExist as e:
        return None
    
def get_untranslated_sentance():
    try:
        untaranslated = TranslatedSentance.objects.filter(is_translated=False).first()
        return untaranslated
    except TranslatedSentance.DoesNotExist as e:
        return None

def get_lines(page_id):
    try:
        page = Page.objects.get(pk=page_id)
        data = json.loads(page.ocr)
        if not data or 'level' not in data:
            return None

        for i, level in enumerate(data['level']):
            if level == 1:
                img_width = data['width'][i]
                img_height = data['height'][i]
                break
        else:
            return None
        
        lines = []

        for i, level in enumerate(data['level']):
            if level != 4:
                continue

            left = data['left'][i]
            top = data['top'][i]
            width = data['width'][i]
            height = data['height'][i]

            left_pct = (left / img_width) * 100
            top_pct = (top / img_height) * 100
            width_pct = (width / img_width) * 100
            height_pct = (height / img_height) * 100

            css = {
                'left': f"{left_pct:.4f}%",
                'top': f"{top_pct:.4f}%",
                'width': f"{width_pct:.4f}%",
                'height': f"{height_pct:.4f}%"
            }

            lines.append(css)

        return lines
    except Page.DoesNotExist as e:
        return None


def save_translations(translations):
    try:
        sentance = TranslatedSentance.objects.get(pk=translations['sentance_id'])
        langs = ['en', 'he', 'ru', 'ua']
        try:
            for lang in langs:
                translation = Translation(
                    translation=translations[lang],
                    sentance=sentance,
                    language=lang
                )
                translation.save()
            sentance.is_translated = True
            sentance.save()
        except:
            return None
        return sentance.pk
    except TranslatedSentance.DoesNotExist as e:
        return None
    
def get_for_sref(sref):
    try:
        first_anchor = PageAnchor.objects.filter(sefaria_ref=sref).first()
        page = first_anchor.page
        return get_page_data(page)
    except (PageAnchor.DoesNotExist, AttributeError) as e:
        return None