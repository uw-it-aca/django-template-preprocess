import os
from django.template import Context, Template

BASE_SETTINGS = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': '',
        'APP_DIRS': True,
    }
]


def get_test_template_settings():
    test_path = os.path.join(os.path.dirname(__file__), 'test_templates')
    static_path = os.path.join(os.path.dirname(__file__), 'test_statics')

    finders = ['django.contrib.staticfiles.finders.FileSystemFinder',
               'compressor.finders.CompressorFinder']

    BASE_SETTINGS[0]['DIRS'] = [test_path]
    return {'TEMPLATES': BASE_SETTINGS,
            'COMPRESS_ENABLED': True,
            'COMPRESS_OFFLINE': False,
            'COMPRESS_ROOT': './compress-test',
            'STATICFILES_DIRS': [static_path],
            'STATICFILES_FINDERS': finders,
            'STATIC_URL': '/static/',
            }
