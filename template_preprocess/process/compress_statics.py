from django.template import Template, Context
import re


def process(content, seen_templates, template_processor):
    def replace_compress_block(match):
        template_string = "{% load compress %}{% load static %}"+match.group(0)
        t = Template(template_string)
        c = Context({})
        value = t.render(c)
        return value

    content = re.sub(r'{%\s*compress\s+.*?%}(.*?){%\s*endcompress\s*%}',
                     replace_compress_block,
                     content, flags=re.DOTALL)

    return content
