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

    # Transform GitHub asset URLs to use our proxy
    def transform_image_urls(text):
        # Pattern to match GitHub asset URLs
        pattern = r'(https://github\.com/([^)\s]+/assets/[^)\s]+))'

        def replace_url(match):
            full_url = match.group(1)
            asset_path = match.group(2)
            # Use our proxy endpoint
            return reverse('proxy_github_asset', kwargs={'path': asset_path})

        return re.sub(pattern, replace_url, text)

    # Transform URLs before processing markdown
    text = transform_image_urls(text)

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
