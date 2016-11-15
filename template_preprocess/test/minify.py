from django.test import TestCase
from django.test.utils import override_settings
from template_preprocess.processor import process_template_content
from template_preprocess.test import get_test_template_settings


template_settings = get_test_template_settings()


@override_settings(**template_settings)
class TestHTMLMinify(TestCase):
    def test_minify_fragment(self):
        content = "<b>  <i></i>   \n</b>"
        result = process_template_content(content, is_html=True)

        self.assertEquals(result, "<b><i></i></b>")
