from django.test import TestCase
from django.test.utils import override_settings
from template_preprocess.processor import process_template_content
from template_preprocess.test import get_test_template_settings


template_settings = get_test_template_settings()


@override_settings(**template_settings)
class TestExtendBlock(TestCase):
    def test_basic_block(self):
        content = '{% include "extends/sub_template1.html" %}'
        result = process_template_content(content)

        correct = ('Before {% block inserted_content %}The Block'
                   '{%endblock inserted_content%} {% block block2 %}'
                   'Block 2{%endblock block2 %} {% block notreplaced %}'
                   'In wrapper{%endblock%} After ')
        self.assertEquals(result, correct)

    def test_extends_missing_template(self):
        content = '{% include "extends/parent_is_missing.html" %}'
        result = process_template_content(content)
        self.assertEquals(result, content)

    def test_recursive_extends(self):
        content = '{% include "extends/recursive.html" %}'
        result = process_template_content(content)
        self.assertEquals(result, content)

    def test_nested_blocks(self):
        content = '{% include "extends/nested.html" %}'
        result = process_template_content(content)
        self.assertEquals(
            result,
            '{% block a %}{% block b %}{% endblock b %}{% endblock %} ')

    def test_load_tag_outside_of_block(self):
        content = '{% include "extends/load_tag_out_of_block.html" %}'
        result = process_template_content(content)

        correct = ('{% load another more from app.templatetags %}'
                   '{% load i18n %}Before {% block content %}'
                   'The content{% endblock %} After ')
        self.assertEquals(result, correct)

    def test_multiline_block(self):
        content = '{% include "extends/multiline.html" %}'
        result = process_template_content(content)

        correct = 'Before {%block ok%}Line 1 Line 2{%endblock%} '

        self.assertEquals(result, correct)
