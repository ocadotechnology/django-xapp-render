'''setup.py for django-xapp-render'''
from setuptools import setup, find_packages
from gitversion import get_git_version

setup(
    name                 = 'django-xapp-render',
    version              = get_git_version(__file__),
    description          = 'Cross app rendering utilities.',
    long_description     = '''Cross app rendering utilities.''',
    author               = 'Netnix',
    author_email         = 'netnix@ocado.com',
    maintainer           = 'Mike Bryant',
    maintainer_email     = 'mike.bryant@ocado.com',
    packages             = find_packages(),
    install_requires     = ['django >= 1.4', 'coffin', 'jinja2'],
    tests_require        = ['coffin', 'jinja2'],
)
