[![Build Status](https://api.travis-ci.org/uw-it-aca/django-template-preprocess.svg?branch=master)](https://travis-ci.org/uw-it-aca/django-template-preprocess)
[![Coverage Status](https://coveralls.io/repos/uw-it-aca/django-template-preprocess/badge.png?branch=master)](https://coveralls.io/r/uw-it-aca/django-template-preprocess?branch=master)

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


You can optionally configure a custom list of preprocessors.  The default is below:

    TEMPLATE_PREPROCESS_PROCESSORS = [
            {"method": "template_preprocess.process.extends.handle_extends"},
            {"method": "template_preprocess.process.includes.handle_includes"},
            {"method": "template_preprocess.process.compress_statics.process", "html_only": True},
            {"method": "template_preprocess.process.html_minify.process", "html_only": True},
            {"method": "template_preprocess.process.static.handle_static_tag", "html_only": True},
            # minify won't minify content in <script> tags, so this needs
            # to be the last thing done
            {"method": "template_preprocess.process.handlebars.process"},
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



