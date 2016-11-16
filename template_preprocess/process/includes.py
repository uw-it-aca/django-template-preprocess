import re


def handle_includes(content, seen_templates, template_processor):
    def insert_template(match):
        name = match.group(1)

        if name in seen_templates:
            raise Exception("Recursive template includes")

        seen_templates[name] = True

        content = template_processor(name, seen_templates)
        return content

    content = re.sub(r"""{%\s*include\s*['"]([^"']+?)["']\s*%}""",
                     insert_template,
                     content, flags=re.UNICODE)

    return content
