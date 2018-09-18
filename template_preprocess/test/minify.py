from django.test import TestCase
from django.test.utils import override_settings
from template_preprocess.processor import process_template_content
from template_preprocess.test import get_test_template_settings


template_settings = get_test_template_settings()


@override_settings(**template_settings)
class TestHTMLMinify(TestCase):
    def test_minify_fragment(self):
        # Needs to be unicode content from htmlmin
        content = u"<b>  <i ></i>   \n</b>"
        result = process_template_content(content, is_html=True)

        self.assertEquals(result, "<b> <i></i> </b>")

    def test_handlebars_safety(self):
        content = (u'<div {{#if has_6_days}}class="six-day"{{else}}'
                   u'class="five-day"{{/if}}></div>'
                   u'<div {{#if has_6_days}}class="six-day"{{else}}'
                   u'class="five-day"{{ /if }}></div>')
        result = process_template_content(content, is_html=True)

        correct = (u'<div {{#if has_6_days}}class=six-day {{else}}'
                   u'class=five-day {{/if}}></div>'
                   u'<div {{#if has_6_days}}class=six-day {{else}}'
                   u'class=five-day {{ /if }}></div>')

        self.assertEquals(result, correct)

    def test_django_statement_safety(self):
        content = (u"""<b {% if search.quarter == 'summer' %} """
                   """selected="selected"{% endif %} />""")

        result = process_template_content(content, is_html=True)
        expected = (u"<b {% if search.quarter == 'summer' %} "
                    u"selected=selected {% endif %} />")
        self.assertEquals(result, expected)

        content = u"""<input type="text" value="{{ foo.bar }}">"""
        result = process_template_content(content, is_html=True)
        self.assertEquals(result, '<input type=text value="{{ foo.bar }}">')

        content = u"""<input type="text" value='{{ foo.bar }}'>"""
        result = process_template_content(content, is_html=True)
        self.assertEquals(result, "<input type=text value='{{ foo.bar }}'>")

    def test_nested_statement_safety(self):
        content = u"""<div class="{{#if a}}a{{else}}b{{/if}}">"""

        result = process_template_content(content, is_html=True)

        self.assertEquals(result, '<div class="{{#if a}}a{{else}}b{{/if}}">')
