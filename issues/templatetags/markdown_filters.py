from django import template
from django.utils.safestring import mark_safe
import markdown2

register = template.Library()


@register.filter(name='markdown')
def markdown_filter(text):
    if not text:
        return ''
    # Use GitHub-flavored markdown and enable extras including link-patterns for auto-linking
    return mark_safe(markdown2.markdown(text, extras=['fenced-code-blocks', 'tables', 'break-on-newline']))
