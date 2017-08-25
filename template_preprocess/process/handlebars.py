import re
from django.template import Template, Context
from django.conf import settings

# The default values for the exempt django template functions/variables
# that will not be processes when in handlebars functions on the preprocess
DEFAULT_EXEMPT_HANDLEBARS_VARIABLES = ["csrf_token"]


def process(content, seen_templates, template_processor):
    def replace_handlebars(match):
        template_string = ("{% load templatetag_handlebars %}"
                           "{% load static %}"+match.group(0))

        handlebars_variables = getattr(settings,
                                       'EXEMPT_HANDLEBARS_VARIABLES',
                                       DEFAULT_EXEMPT_HANDLEBARS_VARIABLES)

        for variable in handlebars_variables:
            target_regex = r"{%\s*" + variable + "\s*%}"
            target_replace = "{___" + variable + "___}"
            template_string = re.sub(target_regex, target_replace,
                                     template_string)

        t = Template(template_string)
        c = Context({})
        value = t.render(c)

        for variable in handlebars_variables:
            target_string = "{___" + variable + "___}"
            replacement_string = ("{% endverbatim %} {% " + variable + " %}" +
                                  " {% verbatim %}")
            value = value.replace(target_string, replacement_string)

        return "{% verbatim %}" + value + "{% endverbatim %}"

    regex = r'{%\s*tplhandlebars\s+[^\s]+\s*%}(.*?){%\s*endtplhandlebars\s*%}'
    content = re.sub(regex,
                     replace_handlebars,
                     content, flags=re.DOTALL)

    return content
