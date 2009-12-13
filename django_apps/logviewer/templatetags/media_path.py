import urlparse
import os.path

from django.conf import settings
from django.template import Library

def media_path(path):
    # Copied from http://www.djangosnippets.org/snippets/198/
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, path)):
        return urlparse.urljoin(settings.MEDIA_URL, path)
    return ''
    
def js_path(js):
    return (settings.DEBUG and media_path("javascript/%s-full.js" % js)) or media_path("javascript/%s.js" % js)

register = Library()
register.simple_tag(media_path)
register.simple_tag(js_path)

