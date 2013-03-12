'''Signals provided by xapp_render.'''

import django.dispatch

#: Receivers to this signal should return rendered data as a string.
RENDER_REQUESTED = django.dispatch.Signal(providing_args=['context'])

#: Receivers to this signal should return a Form subclass
FORM_REQUESTED = django.dispatch.Signal()
