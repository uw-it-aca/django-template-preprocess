from django.test import TestCase
from django.test.utils import override_settings
from template_preprocess.processor import process_template_content
from template_preprocess.test import get_test_template_settings


template_settings = get_test_template_settings()


@override_settings(**template_settings)
class TestStaticTag(TestCase):
    @override_settings(STATIC_URL="/non-standard/path/")
    def test_static_tag(self):
        content = '{% static "some/file.css" %}'
        result = process_template_content(content, is_html=True)

        correct = "/non-standard/path/some/file.css"
        self.assertEquals(result, correct)
