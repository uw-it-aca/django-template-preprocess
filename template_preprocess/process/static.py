from django.template import Template, Context
import re


def handle_static_tag(content, seen_templates, template_processor):
    def replace_static_url(match):
        template_string = "{% load static %}"+match.group(0)
        t = Template(template_string)
        c = Context({})
        value = t.render(c)
        return value

    content = re.sub(r'{%\s*static\s*[^%]+?%}',
                     replace_static_url,
                     content, flags=re.DOTALL)

    return content
