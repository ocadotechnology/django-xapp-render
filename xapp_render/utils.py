'''Utilities for xapp_render.'''

from django.dispatch import receiver
from functools import wraps

from .signals import RENDER_REQUESTED, FORM_REQUESTED

# We like magic!
# pylint: disable=W0142

def xapp_receiver(identifier, **kwargs):
    """
    A decorator for connecting receivers to the RENDER_REQUESTED signal.
    Used by passing in the identifier you want to render for.
    """
    def function_decorator(func):
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
    return function_decorator

def xapp_form(identifier, **kwargs):
    '''
    A class decorator, which will result in the class being
    passed when asked for by the FORM_REQUESTED signal.
    '''
    def class_decorator(klass):
        '''Decorate the class.'''

        @receiver(FORM_REQUESTED, **kwargs)
        def form_receiver(sender, *_args, **_kwargs):
            '''When the right identifier is asked for, return this Form.'''
            if sender == identifier:
                return klass
            else:
                return None

        # Deal with weak references
        xapp_receivers = getattr(klass, 'xapp_receivers', [])
        xapp_receivers.append(form_receiver)
        klass.xapp_receivers = xapp_receivers

        return klass

    return class_decorator

def get_xapp_form(identifier):
    '''Return the Form.'''
    possible_parents = []
    parents = []

    for (_receiver, response) in FORM_REQUESTED.send(sender=identifier):
        if response is not None:
            possible_parents.append(response)

    for parent in possible_parents:
        for other_parent in possible_parents:
            if parent is not other_parent and parent in other_parent.mro():
                break
        else:
            # We didn't find it in any of the mros, so we include it.
            parents.append(parent)

    return type('DynamicForm', tuple(parents), {})

def xapp_form_factory(identifier):
    '''Return a callable,
        which will return a Form instance from all the xapp signals.
    '''
    def form_instance(*args, **kwargs):
        '''Instantiate the form.'''
        return get_xapp_form(identifier)(*args, **kwargs)

    return form_instance
