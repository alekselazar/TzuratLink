"""
Language utilities for TzuratLink.
Standardizes language detection and handling across backend and frontend.
"""

def get_language_from_header(accept_language_header):
    """
    Extract language from Accept-Language header.
    Returns either 'en' or 'he' (Hebrew for any non-English).
    
    Args:
        accept_language_header: Accept-Language HTTP header string
    
    Returns:
        str: 'en' or 'he' (default)
    """
    if not accept_language_header:
        return 'he'
    
    # Parse Accept-Language header (e.g., "en-US,en;q=0.9,he;q=0.8")
    languages = accept_language_header.lower().split(',')
    
    for lang in languages:
        # Extract language code (before hyphen if present)
        lang_code = lang.split(';')[0].split('-')[0].strip()
        
        if lang_code == 'en':
            return 'en'
        elif lang_code == 'he':
            return 'he'
    
    # Default to Hebrew for any other language
    return 'he'


def get_language_direction(lang):
    """
    Get text direction for language.
    
    Args:
        lang: 'en' or 'he'
    
    Returns:
        str: 'ltr' (left-to-right) or 'rtl' (right-to-left)
    """
    return 'ltr' if lang == 'en' else 'rtl'
