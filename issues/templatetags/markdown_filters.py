from django import template
from django.utils.safestring import mark_safe
import markdown2
import re

register = template.Library()


@register.filter(name='markdown')
def markdown_filter(text):
    if not text:
        return ''

    # Define URL patterns for automatic linking
    url_patterns = [
        # Match URLs not already in markdown link format
        (re.compile(r'(?<![\(\[])((https?|ftp)://[^\s<>]+[^\s.,<>)\]\'"!?])'), r'\1'),
    ]

    # Use GitHub-flavored markdown and enable extras including images and link handling
    return mark_safe(markdown2.markdown(text, extras={
        'fenced-code-blocks': None,
        'tables': None,
        'break-on-newline': None,
        'cuddled-lists': None,
        'target-blank-links': None,
        'header-ids': None,
        'strike': None,
        'task_list': None,
        'images': None,  # Enable image processing
        'html-classes': None,  # Add CSS classes to HTML elements
        'code-friendly': None,  # Better code handling
        'safe': None,  # Allow raw HTML to pass through
        'link-patterns': url_patterns  # Enhanced URL pattern matching with patterns
    }))
