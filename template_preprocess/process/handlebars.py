import re
from django.template import Template, Context


def process(content, seen_templates, template_processor):
    def replace_handlebars(match):
        template_string = ("{% load templatetag_handlebars %}"
                           "{% load static %}"+match.group(0))
        t = Template(template_string)
        c = Context({})
        value = t.render(c)
        return "{% verbatim %}" + value + "{% endverbatim %}"

    regex = r'{%\s*tplhandlebars\s+[^\s]+\s*%}(.*?){%\s*endtplhandlebars\s*%}'
    content = re.sub(regex,
                     replace_handlebars,
                     content, flags=re.DOTALL)

    return content
