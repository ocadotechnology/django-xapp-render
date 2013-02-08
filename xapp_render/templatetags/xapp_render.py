'''xapp_render templatetag'''
# We require the 'register' variable for django to recognise this library
# pylint: disable=C0103

from django import template

from ..template_utils import render_content

register = template.Library()


@register.simple_tag(takes_context=True)
def xapp_render(context, identifier):
    '''
        Takes an identifier, and renders the correct content for that
        identifier.
    '''

    return render_content(identifier, context)
