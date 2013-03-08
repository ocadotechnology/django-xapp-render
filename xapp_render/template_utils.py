'''Utilities for the template tags to use.'''

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

import logging
LOGGER = logging.getLogger(__name__)

#: Holds the template cache
#: The keys are xapp identifiers, and the value
#: is a list of valid templates
TEMPLATE_CACHE = {}

def render_content(identifier, context):
    '''Find all the appropriate chunks of content and render them.'''

    content = ''
    working_modules = []

    cached_modules = TEMPLATE_CACHE.get(identifier, settings.INSTALLED_APPS)

    for module in cached_modules:
        short_name = module.split('.')[-1]
        template_name = "%s/%s" % (short_name, identifier)
        try:
            content += render_to_string(template_name, context)
            working_modules.append(module)
        except TemplateDoesNotExist as err:
            missing_name = err.args[0]
            if missing_name == template_name:
                LOGGER.debug(
                    "Template %s not found during xapp_render",
                    template_name,
                )
            else:
                raise

    if identifier not in TEMPLATE_CACHE:
        TEMPLATE_CACHE[identifier] = working_modules

    return content

def reset_cache():
    '''Reset the template cache.'''
    TEMPLATE_CACHE.clear()
