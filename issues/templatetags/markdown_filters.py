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
    'img': ['src', 'alt', 'title', 'width', 'height', 'style'],
    'code': ['class'],
    'pre': ['class'],
    '*': ['class']
}

@register.filter(name='markdown')
def markdown_filter(text):
    if not text:
        return ''

    # Clean up malformed image tags and convert to proper markdown
    def clean_image_tags(text):
        # Remove any malformed <a rel=> tags
        text = re.sub(r'<a rel=">', '', text)
        # Remove any malformed HTML entities
        text = text.replace('&gt;', '>')
        # Extract image URLs and their attributes
        img_pattern = r'<img src="([^"]+)"([^>]*)/?>'
        
        def replace_img(match):
            url = match.group(1)
            attrs = match.group(2).strip()
            # Convert width attribute if present
            width_match = re.search(r'width="([^"]+)"', attrs)
            width_style = f' style="width: {width_match.group(1)};"' if width_match else ''
            return f'<img src="{url}"{width_style} alt="">'
            
        text = re.sub(img_pattern, replace_img, text)
        return text

    # Process the text
    text = clean_image_tags(text)

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
        'code-friendly': None
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
