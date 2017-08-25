from django.test import TestCase
from template_preprocess.process.handlebars import process


class TestHandlebars(TestCase):

    def test_exempt_tag(self):
        original = '{% tplhandlebars "request_email_lists_tmpl" %} {% csrf_token %} {% endtplhandlebars %}'
        target = u'{% verbatim %}\n        <script type="text/x-handlebars-template" id="request_email_lists_tmpl">\n         {% endverbatim %} {% csrf_token %} {% verbatim %} \n        </script>{% endverbatim %}'

        result = process(original, None, None)

        self.assertEquals(result, target)

        with self.settings(EXEMPT_HANDLEBARS_VARIABLES=['csrf_token', 'netid']):
            original = '{% tplhandlebars "request_email_lists_tmpl" %} {% csrf_token %} {% netid %} {% endtplhandlebars %}'
            target = u'{% verbatim %}\n        <script type="text/x-handlebars-template" id="request_email_lists_tmpl">\n         {% endverbatim %} {% csrf_token %} {% verbatim %} {% endverbatim %} {% netid %} {% verbatim %}\n        </script>{% endverbatim %}'
            result = process(original, None, None)
            self.assertEquals("result, target")
