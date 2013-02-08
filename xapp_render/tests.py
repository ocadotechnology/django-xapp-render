"""
Tests for xapp_render
"""

# pylint: disable=R0904
# pylint: disable=C0103

import os
import shutil
import sys
import tempfile

from django.core.management import call_command
import django.template.loader
from django.template.loader import render_to_string
import django.template.loaders.app_directories
from django.test import TestCase
from django.test.utils import override_settings


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
        ),
        'xapp_test_app_2': (
            ('test1.html', '{% ifequal True True %}Flibble{% endifequal %}'), #Need to be sure we're in django
        ),
        'xapp_test_app_3': (
            ('test1.html', 'Dribble'),
        ),
    }

    def test_content(self):
        '''Test if rendering the templates includes the content'''
        self.assertIn('FlibbleDribble', render_to_string('xapp_test_app_1/base.html', {}))


@override_settings(
    INSTALLED_APPS=['xapp_render', 'xapp_test_app_4', 'xapp_test_app_5', 'xapp_test_app_6'],
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

    apps = ['xapp_test_app_4', 'xapp_test_app_5', 'xapp_test_app_6']
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
