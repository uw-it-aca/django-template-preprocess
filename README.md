Django Template Preprocessor
============================

A tool for processing templates during a deployment.  This does require each deployment write out to a new preprocessed directory.


Add settings like this to your project:


COMPILED_TEMPLATE_PATH = '/tmp/templates/compiled/next_build'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            COMPILED_TEMPLATE_PATH,
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


Add 'template_preprocess' to your INSTALLED_APPS, and you can run:

  python manage.py preprocess_templates


Currently supports:


* Extended templates with block content
* Includes
* HTML minification
* Django-compressor blocks
* django-templatetag-handlebars
* static url tags

Coming up(?):



