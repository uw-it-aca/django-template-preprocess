import os
from django.template import Context, Template

BASE_SETTINGS = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': '',
    }
]


def get_test_template_settings():
    test_path = os.path.join(os.path.dirname(__file__), 'test_templates')

    BASE_SETTINGS[0]['DIRS'] = [test_path]
    return {'TEMPLATES': BASE_SETTINGS}
