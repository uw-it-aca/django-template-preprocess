from django.test import TestCase
from django.test.utils import override_settings
from template_preprocess.processor import process_template_content
from template_preprocess.test import get_test_template_settings


template_settings = get_test_template_settings()


@override_settings(**template_settings)
class TestIncludeBlock(TestCase):
    def test_include(self):
        content = '{%include "includes/include1.html"%}'
        result = process_template_content(content)

        self.assertEquals(result, "included template ")

    def test_single_quotes(self):
        content = "{%include 'includes/include1.html'%}"
        result = process_template_content(content)

        self.assertEquals(result, "included template ")

    def test_nested(self):
        content = '{%include "includes/nested_1.html"%}'
        result = process_template_content(content)

        self.assertEquals(result, "1 2 ")

    def test_recursion(self):
        content = '{%include "includes/include_recursion.html"%}'
        result = process_template_content(content)

        self.assertEquals(result, content)

    def test_error_include(self):
        content = '{%include "includes/DOESNT_EXIST.html"%}'
        result = process_template_content(content)

        self.assertEquals(result, content)
