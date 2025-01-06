from django import template
from django.utils.safestring import mark_safe
import markdown2
import re
import bleach

register = template.Library()

ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'p',
    'strong', 'ul', 'br', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'table', 'tbody', 'thead', 'tr', 'td', 'th', 'img', 'pre', 'del', 'sup', 'sub'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title'],
    'code': ['class'],
    'pre': ['class'],
    '*': ['class']
}

@register.filter(name='markdown')
def markdown_filter(text):
    if not text:
        return ''

    # Define URL patterns for automatic linking
    url_patterns = [
        # Match URLs not already in markdown link format
        (re.compile(r'(?<![\(\[])((https?|ftp)://[^\s<>]+[^\s.,<>)\]\'"!?])'), r'\1'),
    ]

    # Convert markdown to HTML
    html = markdown2.markdown(text, extras={
        'fenced-code-blocks': None,
        'tables': None,
        'break-on-newline': None,
        'cuddled-lists': None,
        'target-blank-links': None,
        'header-ids': None,
        'strike': None,
        'task_list': None,
        'images': None,
        'html-classes': None,
        'code-friendly': None,
        'link-patterns': url_patterns
    })

    # Sanitize the HTML
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=['http', 'https', 'mailto'],
        strip=True
    )

    return mark_safe(clean_html)
