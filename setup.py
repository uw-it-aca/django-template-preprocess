import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/django-template-preprocess>`_.
"""

# The VERSION file is created by travis-ci, based on the tag name
version_path = 'template_preprocess/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

url = "https://github.com/uw-it-aca/django-template-preprocess"
setup(
    name='Django-Template-Preprocess',
    version=VERSION,
    packages=['template_preprocess'],
    author="UW-IT AXDD",
    author_email="aca-it@uw.edu",
    include_package_data=True,
    install_requires=[
        'Django>2.1,<3.0',
        'django-compressor',
        'htmlmin',
    ],
    license='Apache License, Version 2.0',
    description=('Cut down on django template CPU time by doing work early.'),
    long_description=README,
    url=url,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)

