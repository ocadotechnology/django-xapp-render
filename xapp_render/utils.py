'''Utilities for xapp_render.'''

from django.dispatch import receiver
from functools import wraps

from .signals import RENDER_REQUESTED

# We like magic!
# pylint: disable=W0142

def xapp_receiver(identifier, **kwargs):
    """
    A decorator for connecting receivers to the RENDER_REQUESTED signal.
    Used by passing in the identifier you want to render for.
    """
    def _decorator(func):
        '''Decorator function.'''
        @receiver(RENDER_REQUESTED, **kwargs)
        @wraps(func)
        def wrapper(sender, context, *_args, **_func_kwargs):
            '''Wrapper for the function, only executes if the sender matches
                the identifier.
            '''
            if sender == identifier:
                return func(context)
            else:
                return ''
        return wrapper
    return _decorator

