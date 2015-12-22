DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
}
ROOT_URLCONF = 'django_autoconfig.autourlconf'
INSTALLED_APPS = ['xapp_render',]
STATIC_URL = '/static/'
STATIC_ROOT = ''
