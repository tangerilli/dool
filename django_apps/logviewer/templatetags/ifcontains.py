from django.template import Library
from django import template

def do_ifcontains(parser, token):
    tag_name, key, container = token.split_contents()
    nodelist = parser.parse(('endifcontains',))
    parser.delete_first_token()
    return IfContainsNode(nodelist, key, container)

class IfContainsNode(template.Node):
    def __init__(self, nodelist, key, container):
        self.nodelist = nodelist
        self.key = template.Variable(key)
        self.container = template.Variable(container)
        
    def render(self, context):
        output = self.nodelist.render(context)
        key = self.key.resolve(context)
        container = self.container.resolve(context)
        if key in container:
            return output
        else:
            return ''
    
register = Library()
register.tag('ifcontains', do_ifcontains)