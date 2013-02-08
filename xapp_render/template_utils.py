'''Utilities for the template tags to use.'''

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

import logging
LOGGER = logging.getLogger(__name__)

def render_content(identifier, context):
    '''Find all the appropriate chunks of content and render them.'''

    content = ''

    for module in settings.INSTALLED_APPS:
        short_name = module.split('.')[-1]
        template_name = "%s/%s" % (short_name, identifier)
        try:
            content += render_to_string(template_name, context)
        except TemplateDoesNotExist:
            LOGGER.debug(
                "Template %s not found during xapp_render",
                template_name
            )

    return content
