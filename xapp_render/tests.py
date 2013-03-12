"""
Tests for xapp_render
"""

# pylint: disable=R0904
# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=W0232
# pylint: disable=R0903

import mock
import os
import shutil
import sys
import tempfile

from django.core.management import call_command
from django.dispatch import receiver
from django import forms
from django.template import TemplateDoesNotExist
import django.template.loader
from django.template.loader import render_to_string
import django.template.loaders.app_directories
from django.test import TestCase
from django.test.signals import setting_changed
from django.test.utils import override_settings

from .template_utils import reset_cache
from .utils import xapp_receiver, xapp_form, xapp_form_factory, get_xapp_form

@receiver(setting_changed)
def cache_reset_handler(*_args, **_kwargs):
    '''Reset the cache whenever we change installed apps.'''
    reset_cache()

@xapp_receiver('test5.html')
def test5_rendered_data(context):
    '''Respond with some data rendered from the context.'''
    return render_to_string('xapp_test_app_1/test5_data.html', context)

@xapp_form('form1')
@xapp_form('form3')
class FormA(forms.Form):
    field_a = forms.CharField()

@xapp_form('form2')
class FormB(forms.Form):
    field_b = forms.CharField()

@xapp_form('form2')
class FormC(forms.Form):
    field_c = forms.CharField()

@xapp_form('form3')
class FormD(forms.Form):
    field_d = forms.CharField()

@xapp_form('form3')
class FormE(FormD):
    field_e = forms.CharField()

class FormTestCase(TestCase):
    '''Test form functionality.'''

    def test_single_form(self):
        form = xapp_form_factory('form1')()
        self.assertIn('field_a', form.fields)

    def test_multiple_forms(self):
        form = get_xapp_form('form2')()
        self.assertIn('field_b', form.fields)
        self.assertIn('field_c', form.fields)
        self.assertNotIn('field_a', form.fields)

    def test_conflicting_mro(self):
        form = get_xapp_form('form3')()
        self.assertIn('field_a', form.fields)
        self.assertIn('field_d', form.fields)
        self.assertIn('field_e', form.fields)

class AppCreatorTestCase(TestCase):
    '''Test case that creates some extra apps.'''

    apps = []
    templates = {}

    def setUp(self):
        reload(django.template.loaders.app_directories)
        django.template.loader.template_source_loaders = None

    @classmethod
    def setUpClass(cls):
        """
        Create the apps.
        """
        cls.app_directory = tempfile.mkdtemp()
        for app_name in cls.apps:
            app_dir = "%s/%s" % (cls.app_directory, app_name)
            os.mkdir(app_dir)
            call_command('startapp', app_name, app_dir)
            os.mkdir("%s/templates" % app_dir)
            template_dir = "%s/templates/%s" % (app_dir, app_name)
            os.mkdir(template_dir)

            try:
                for template_name, template_content in cls.templates[app_name]:
                    with open("%s/%s" % (template_dir, template_name), 'w') as fobj:
                        fobj.write(template_content)
            except KeyError:
                pass

        sys.path.insert(0, cls.app_directory)

    @classmethod
    def tearDownClass(cls):
        """Clear up the apps"""
        sys.path.remove(cls.app_directory)
        shutil.rmtree(cls.app_directory)

@override_settings(
    INSTALLED_APPS=['xapp_render', 'xapp_test_app_1', 'xapp_test_app_2', 'xapp_test_app_3'],
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ),
)
class DjangoTestCase(AppCreatorTestCase):
    '''Test the simple case, with only templates'''

    apps = ['xapp_test_app_1', 'xapp_test_app_2', 'xapp_test_app_3']
    templates = {
        'xapp_test_app_1': (
            ('base.html', '{% load xapp_render %}{% xapp_render "test1.html" %}'),
            ('base2.html', '{% load xapp_render %}{% xapp_render "test4.html" %}'),
            ('base3.html', '{% load xapp_render %}{% xapp_render "test5.html" %}'),
            ('test5_data.html', 'Data5: {{ context_data5 }}'),
        ),
        'xapp_test_app_2': (
            ('test1.html', '{% ifequal True True %}Flibble{% endifequal %}'), #Need to be sure we're in django
            ('test4.html', '{% include "notexist.html" %}'),
        ),
        'xapp_test_app_3': (
            ('test1.html', 'Dribble'),
        ),
    }

    def test_content(self):
        '''Test if rendering the templates includes the content'''
        self.assertIn('FlibbleDribble', render_to_string('xapp_test_app_1/base.html', {}))

    def test_signals(self):
        '''Test signals functionality.'''
        result = render_to_string('xapp_test_app_1/base3.html', {'context_data5': 'XXYYZZ5'})
        self.assertIn('Data5: XXYYZZ5', result)
        self.assertNotIn('Data5: XXYYZZ5', render_to_string('xapp_test_app_1/base.html', {'context_data5': 'XXYYZZ5'}))

    def test_broken_templates(self):
        '''We want to raise TemplateDoesNotExist if the reason behind
            one of the xapp templates not existing is because it includes
            something broken.
        '''
        with self.assertRaises(TemplateDoesNotExist):
            render_to_string('xapp_test_app_1/base2.html', {})

def broken_open(*_args, **_kwargs):
    '''Break open completely.'''
    raise Exception

@override_settings(
    INSTALLED_APPS=['xapp_render', 'xapp_test_app_8', 'xapp_test_app_9', 'xapp_test_app_10'],
    TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader', (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        )),
    ),
)
class CachedTestCase(AppCreatorTestCase):
    '''Test caching of templates.'''

    apps = ['xapp_test_app_8', 'xapp_test_app_9', 'xapp_test_app_10']
    templates = {
        'xapp_test_app_8': (
            ('base.html', '{% load xapp_render %}{% xapp_render "test3.html" %}'),
        ),
        'xapp_test_app_9': (
            ('test3.html', 'Blah'),
        ),
        'xapp_test_app_10': (
        ),
    }

    def test_caching(self):
        '''Test if the missing template caching code is working.'''
        # If we're not doing negative caching we'll hit the open call, and things will break
        reset_cache()
        with mock.patch('__builtin__.open', broken_open):
            with self.assertRaises(Exception):
                render_to_string('xapp_test_app_8/base.html', {})

        self.assertIn('Blah', render_to_string('xapp_test_app_8/base.html', {}))
        with mock.patch('__builtin__.open', broken_open):
            self.assertIn('Blah', render_to_string('xapp_test_app_8/base.html', {}))



@override_settings(
    INSTALLED_APPS=['xapp_render', 'xapp_test_app_4', 'xapp_test_app_5', 'xapp_test_app_6', 'xapp_test_app_7'],
    TEMPLATE_LOADERS = (
       'coffin.template.loaders.Loader',
    ),
    JINJA2_TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ),
)
class Jinja2TestCase(AppCreatorTestCase):
    '''Test the simple case, with only templates'''

    apps = ['xapp_test_app_4', 'xapp_test_app_5', 'xapp_test_app_6', 'xapp_test_app_7']
    templates = {
        'xapp_test_app_4': (
            ('base2.html', '{% xapp_render "test2.html" %}'),
        ),
        'xapp_test_app_5': (
            ('test2.html', 'Flibble'),
        ),
        'xapp_test_app_6': (
            ('test2.html', 'Dribble'),
        ),
    }

    def test_content(self):
        '''Test if rendering the templates includes the content'''
        self.assertIn('FlibbleDribble', render_to_string('xapp_test_app_4/base2.html', {}))
