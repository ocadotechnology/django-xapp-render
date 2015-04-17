'''setup.py for django-xapp-render'''
from setuptools import setup, find_packages
from xapp_render.version import __VERSION__

setup(
    name                 = 'django-xapp-render',
    version              = __VERSION__,
    description          = 'Cross app rendering utilities.',
    long_description     = '''Cross app rendering utilities.''',
    author               = 'Netnix',
    author_email         = 'netnix@ocado.com',
    maintainer           = 'Mike Bryant',
    maintainer_email     = 'mike.bryant@ocado.com',
    packages             = find_packages(),
    install_requires     = ['django >= 1.4', 'jinja2'],
    tests_require        = ['coffin', 'jinja2', 'mock'],
)
