import base64
import urllib.request, urllib.error

from openai import OpenAI
from dotenv import load_dotenv

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
            data = res.read()
            base64_encoded = base64.b64encode(data).decode('utf-8')
            page = Page(
                file=base64_encoded,
                foreign_url=url,
                reviewed=False,
                completed=False
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
    
def save_sent(page_id, sefaria_ref, text, boxes=[]):
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
        sentance = TranslatedSentance(sentance=text, sefaria_ref=sefaria_ref)
        sentance.save()
        return sentance.pk
    except Page.DoesNotExist as e:
        return None
    
def get_untranslated_sentance():
    try:
        untaranslated = TranslatedSentance.objects.filter(is_translated=False).first()
        return untaranslated
    except TranslatedSentance.DoesNotExist as e:
        return None
    
def get_openai_translations(sentance_id):
    
    load_dotenv('.env')
    client = OpenAI()

    try:
        sentance = TranslatedSentance.objects.get(pk=sentance_id)
        translations = {
            'sentanceId': sentance.pk,
            'sentance': sentance.sentance
        }

        languages = {
            'en': 'English',
            'he': 'Hebrew',
            'ru': 'Russian',
            'ua': 'Ukrainian'
        }

        def translate(text, language, ref):
            try:
                prompt = f'Translate the following talmudic text into {language}, it\'s Sefaria ref is {ref}:\n\n{text}\n\nIf sefaria has translation of it, examine it, and translate according it'
                res = client.responses.create(
                    model="gpt-4o",
                    input=[
                        {'role': 'system',
                         'content': 'You are a masterful translator of classical Jewish texts, including Talmud, Rishonim, and Halachic literature. You deeply understand the nuances of rabbinic Hebrew, Aramaic, and Torah concepts, and can explain them clearly and accurately in multiple languages. When a user gives you a text and a list of target languages, return faithful, well-phrased translations that match the tone and intent of the original. Maintain halachic and philosophical nuance. Adapt the language style. Always preserve references to Torah concepts, halachic debates, and rabbinic phrases. Where the text includes technical or unclear wording, clarify its meaning naturally in translation. If hebrew translation needed, it should be in modern language, understood for every reader. Return the translation only.'},
                        {'role': 'user', 'content': prompt}
                    ] 
                )
                translation = res.output_text
                return translation
            except BaseException as e:
                print(e)
                return None
        for key, value in languages.items():
            translation = translate(sentance.sentance, value, sentance.sefaria_ref)
            if not translation:
                return None
            translations[key] = translation
        return translations
    except TranslatedSentance.DoesNotExist as e:
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
    except PageAnchor.DoesNotExist as e:
        return None