from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse
import markdown2
import re

register = template.Library()


@register.filter(name='markdown')
def markdown_filter(text):
    if not text:
        return ''

    # Use GitHub-flavored markdown and enable extras including images and link handling
    return mark_safe(markdown2.markdown(text, extras=[
        'fenced-code-blocks',
        'tables',
        'break-on-newline',
        'cuddled-lists',
        'target-blank-links',
        'header-ids',
        'strike',
        'task_list',
        'images',  # Enable image processing
        'html-classes',  # Add CSS classes to HTML elements
        'code-friendly',  # Better code handling
        'safe'  # Allow raw HTML to pass through
    ]))
