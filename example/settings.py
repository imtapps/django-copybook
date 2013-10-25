import sys
from os.path import abspath, dirname, join
parent = abspath(dirname(__file__))
grandparent = abspath(join(parent, '..'))
for path in (grandparent, parent):
    if path not in sys.path:
        sys.path.insert(0, path)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

SECRET_KEY = 'foo'

INSTALLED_APPS = (
    'djcopybook',
    'django_nose',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
