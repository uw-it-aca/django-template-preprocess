import re
from django.test import TestCase
from django.test.utils import override_settings
from template_preprocess.processor import process_template_content
from template_preprocess.test import get_test_template_settings

template_settings = get_test_template_settings()


@override_settings(**template_settings)
class TestCompressTag(TestCase):
    def test_basic(self):
        content = (
            u'{% compress css %}<link rel="stylesheet" '
            u'href="/static/foo.css">{% endcompress %}')
        result = process_template_content(content, is_html=True)

        self.assertTrue(
            re.match(
                r'<link rel=stylesheet href=/static/CACHE/css/[a-z0-9]+.css',
                result))

    def test_inline(self):
        content = (
            u'{% compress css inline %}<link rel="stylesheet" '
            u'href="/static/foo.css">{% endcompress %}')
        result = process_template_content(content, is_html=True)

        self.assertEquals(
            '<style type=text/css>#foo { color: red; }\n</style>', result)
