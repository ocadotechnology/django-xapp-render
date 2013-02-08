'''xapp_render templatetag for Jinja2'''
# We require the 'register' variable for django to recognise this library
# pylint: disable=C0103

from coffin import template
import jinja2
from jinja2.ext import Extension

from ..template_utils import render_content

register = template.Library()


@register.tag()
class XappRenderExtension(Extension):
    '''
        Takes an identifier, and renders the correct content for that
        identifier.
    '''

    tags = set(['xapp_render'])

    def parse(self, parser):
        # This is the xapp_render tag token.
        token = parser.stream.next()

        # This is the identifier
        args = [parser.parse_expression()]

        return jinja2.nodes.CallBlock(
            self.call_method('_xapp_support', args),
            [], [], []
        ).set_lineno(token.lineno)

    @jinja2.contextfunction
    def _xapp_support(self, context, identifier, caller):
        """Callback for rendering the node."""
        # It needs to be a method for autoloading
        # pylint: disable=R0201

        # caller is passed as a keyword argument, so we can't rename it
        # pylint: disable=W0613

        return render_content(identifier, context)
